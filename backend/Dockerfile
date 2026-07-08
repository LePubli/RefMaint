FROM python:3.11-slim

WORKDIR /app

# No compiler needed: psycopg2-binary, bcrypt, cryptography and pillow all
# ship prebuilt manylinux wheels for this Python/arch, so gcc/libpq-dev were
# unused dead weight here. Removing them cuts unnecessary CPU/network/memory
# load during the build, which matters because Coolify builds backend and
# frontend concurrently (buildx bake) and the combined peak usage was likely
# contributing to intermittent build failures on constrained hosts.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh && mkdir -p /data/uploads

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
