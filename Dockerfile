# Multi-stage build for Go Backend
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY backend-go/ .
RUN go build -ldflags="-s -w" -o fmstar-core

# Final Lightweight Runtime Image
FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/fmstar-core .
EXPOSE 8080
CMD ["./fmstar-core"]
