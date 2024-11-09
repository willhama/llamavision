# Use an official Node.js image as a parent image
FROM node:18-alpine

# Install pnpm
RUN npm install -g pnpm

# Set the working directory inside the container
WORKDIR /app

# Copy package files to the container
COPY pnpm-lock.yaml ./
COPY package.json ./

# Install dependencies using pnpm
RUN pnpm install

# Copy the rest of the application code
COPY . .

# Build the Next.js application
RUN pnpm build

# Expose the port that the app runs on
EXPOSE 3000

# Start the application
CMD ["pnpm", "run", "dev"]