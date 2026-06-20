# NOTE: This hash is pinned to avoid version and environment differences.
FROM julia:1.12.6-trixie@sha256:ab99aafa5e0300dba3ae82d70018265ca62c990265da7a84cc38fe6d1d3adfb5 AS builder

ENV JULIA_DEPOT_PATH=/usr/local/share/julia

RUN apt-get update && \
    apt-get install -y --no-install-recommends socat && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY Project.toml Manifest.toml ./
RUN julia --project=. -e 'using Pkg; Pkg.instantiate(); Pkg.precompile()' && \
    chmod -R a+rX /usr/local/share/julia

COPY app.jl ./

USER nobody:nogroup
CMD ["socat", "-T30", "tcp-listen:1337,fork,reuseaddr", "exec:'julia --project=. app.jl'"]