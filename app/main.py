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
