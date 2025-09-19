from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from .db import Base, engine
from .models import User, ScanResult
from .schemas import UserCreate, UserOut, Token, ScanRequest, ScanResultOut
from .auth import get_db, get_password_hash, authenticate_user, create_access_token, get_current_user

import nmap
import hashlib
import json
import os
from pathlib import Path

app = FastAPI(title="Escudo IA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"status": "ok", "service": "escudo-ia"}

@app.post("/auth/signup", response_model=UserOut, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, hashed_password=get_password_hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token({"sub": user.email, "uid": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/scan/network", response_model=ScanResultOut)
def scan_network(req: ScanRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        nm = nmap.PortScanner()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"nmap is not available on the server: {e}")

    try:
        nm.scan(hosts=str(req.ip), arguments="-F")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scan failed: {e}")

    result = {}
    for host in nm.all_hosts():
        host_data = []
        host_obj = nm[host]
        if hasattr(host_obj, "all_protocols"):
            for proto in host_obj.all_protocols():
                ports_dict = host_obj[proto]
                for port in sorted(ports_dict.keys()):
                    entry = ports_dict[port]
                    state = entry.get("state")
                    name = entry.get("name")
                    product = entry.get("product")
                    version = entry.get("version")
                    host_data.append({
                        "protocol": proto,
                        "port": port,
                        "state": state,
                        "service": name,
                        "product": product,
                        "version": version,
                    })
        else:
            for proto, ports_dict in host_obj.items():
                for port in sorted(ports_dict.keys()):
                    entry = ports_dict[port]
                    state = entry.get("state")
                    name = entry.get("name")
                    product = entry.get("product")
                    version = entry.get("version")
                    host_data.append({
                        "protocol": proto,
                        "port": port,
                        "state": state,
                        "service": name,
                        "product": product,
                        "version": version,
                    })
        result[host] = host_data

    scan = ScanResult(user_id=current_user.id, ip=str(req.ip), scan_payload=result)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan

@app.get("/scan/results", response_model=List[ScanResultOut])
def list_scans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scans = db.query(ScanResult).filter(ScanResult.user_id == current_user.id).order_by(ScanResult.id.desc()).all()
    return scans

@app.get("/license/fingerprint")
def get_license_fingerprint():
    """Generate a unique fingerprint for this system installation"""
    try:
        import platform
        import socket
        
        system_info = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
        
        fingerprint_data = json.dumps(system_info, sort_keys=True)
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
        
        return {
            "fingerprint": fingerprint,
            "system_info": system_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating fingerprint: {e}")

@app.get("/license/status")
def get_license_status():
    """Check the current license status"""
    try:
        license_file = Path("/app/licenses/license.json")
        public_key_file = Path("/app/licenses/public_key.pem")
        
        if not license_file.exists():
            return {
                "valid": False,
                "status": "no_license",
                "message": "No license file found"
            }
        
        if not public_key_file.exists():
            return {
                "valid": False,
                "status": "no_public_key",
                "message": "No public key found"
            }
        
        with open(license_file, 'r') as f:
            license_data = json.load(f)
        
        required_fields = ["fingerprint", "expiry_date", "features"]
        if not all(field in license_data for field in required_fields):
            return {
                "valid": False,
                "status": "invalid_format",
                "message": "License file has invalid format"
            }
        
        current_fingerprint = get_license_fingerprint()["fingerprint"]
        if license_data["fingerprint"] != current_fingerprint:
            return {
                "valid": False,
                "status": "fingerprint_mismatch",
                "message": "License fingerprint does not match system"
            }
        
        from datetime import datetime
        try:
            expiry_date = datetime.fromisoformat(license_data["expiry_date"])
            if datetime.now() > expiry_date:
                return {
                    "valid": False,
                    "status": "expired",
                    "message": "License has expired"
                }
        except ValueError:
            return {
                "valid": False,
                "status": "invalid_date",
                "message": "Invalid expiry date format"
            }
        
        return {
            "valid": True,
            "status": "active",
            "message": "License is valid",
            "license_info": {
                "fingerprint": license_data["fingerprint"],
                "expiry_date": license_data["expiry_date"],
                "features": license_data["features"]
            }
        }
        
    except Exception as e:
        return {
            "valid": False,
            "status": "error",
            "message": f"Error checking license: {e}"
        }
