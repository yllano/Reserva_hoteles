# Use Node 20
FROM node:20-slim

# Set working directory
WORKDIR /app

# Copy package files and install
COPY package*.json ./
RUN npm install --production

# Copy the rest of the code
COPY . .

# Expose port
EXPOSE 8004

# Command to run the application
CMD ["node", "index.js"]
