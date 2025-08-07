FROM node:20

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./

# Limpiar cache y instalar dependencias
RUN npm cache clean --force
RUN npm install

COPY . .

# Verificar que react-scripts esté instalado
RUN ls -la node_modules/.bin/ | grep react-scripts || echo "react-scripts no encontrado"

# Usar el path completo a react-scripts
CMD ["./node_modules/.bin/react-scripts", "start"]
