FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Build the application
RUN npm run build

EXPOSE 3000

ENV NEXT_PUBLIC_API_URL=http://api:8000

CMD ["npm", "start"]
