#!/bin/bash

set -e

echo "🛡️  Escudo IA - Instalación On-Premise"
echo "======================================"

if ! command -v docker &> /dev/null; then
    echo "📦 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker instalado correctamente"
else
    echo "✅ Docker ya está instalado"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Instalando Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose instalado correctamente"
else
    echo "✅ Docker Compose ya está instalado"
fi

if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde .env.example..."
    cp .env.example .env
    
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-secret-key-here-change-this-in-production/$SECRET_KEY/g" .env
    echo "✅ Archivo .env creado con clave secreta generada"
else
    echo "✅ Archivo .env ya existe"
fi

echo "📁 Creando directorios necesarios..."
mkdir -p licenses ops_keys
echo "✅ Directorios creados"

echo "📋 Copiando archivos de la aplicación..."
if [ -d "../app" ]; then
    cp -r ../app ./ 2>/dev/null || true
fi
if [ -d "../frontend" ]; then
    cp -r ../frontend ./ 2>/dev/null || true
fi
if [ -f "../pyproject.toml" ]; then
    cp ../pyproject.toml ./ 2>/dev/null || true
fi
if [ -f "../poetry.lock" ]; then
    cp ../poetry.lock ./ 2>/dev/null || true
fi
echo "✅ Archivos copiados"

echo "🚀 Iniciando servicios..."
docker-compose down 2>/dev/null || true
docker-compose up -d --build

echo "⏳ Esperando que los servicios estén listos..."
sleep 30

echo "🔍 Verificando servicios..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Servicios iniciados correctamente"
    
    if curl -s http://localhost:8000/healthz > /dev/null; then
        echo "✅ Backend funcionando correctamente"
    else
        echo "⚠️  Backend no responde, verificando logs..."
        docker-compose logs escudo_backend
    fi
    
    echo ""
    echo "🔑 Fingerprint del sistema:"
    curl -s http://localhost:8000/license/fingerprint 2>/dev/null || echo "No disponible (requiere implementación de licencias)"
    
    echo ""
    echo "🎉 Instalación completada!"
    echo ""
    echo "📋 Servicios disponibles:"
    echo "   - Frontend: http://localhost"
    echo "   - Backend API: http://localhost:8000"
    echo "   - Health Check: http://localhost:8000/healthz"
    echo ""
    echo "📝 Para obtener el fingerprint: curl -s http://localhost:8000/license/fingerprint"
    echo "📝 Para verificar licencia: curl -s http://localhost:8000/license/status"
    echo ""
    echo "🔧 Para detener: docker-compose down"
    echo "🔧 Para ver logs: docker-compose logs"
    
else
    echo "❌ Error al iniciar servicios"
    docker-compose logs
    exit 1
fi
