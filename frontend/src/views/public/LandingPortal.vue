<script setup>
</script>

<template>
  <div class="split-landing">
    <div class="hero-header">
      <p class="eyebrow">Experiencia premium en la selva</p>
      <p class="hero-text">
        Hospedaje y eventos en un entorno natural, exclusivo y armonioso.
      </p>
    </div>

    <div class="cards-grid">
      <router-link :to="{ name: 'rooms' }" class="split-card hospedaje-side">
        <div class="overlay"></div>
        <div class="card-content">
          <span class="card-label">Hospedaje</span>
          <h2 class="title">Hospedaje Ancestral</h2>
          <p class="subtitle">Confort natural y conexión directa con la selva</p>
          <span class="btn-ingresar">Explorar Hospedaje</span>
        </div>
      </router-link>

      <router-link to="/eventos" class="split-card eventos-side">
        <div class="overlay"></div>
        <div class="card-content">
          <span class="card-label">Eventos</span>
          <h2 class="title">Salón de Eventos</h2>
          <p class="subtitle">Espacios inspiradores para momentos únicos</p>
          <span class="btn-ingresar">Cotizar Eventos</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.split-landing {
  min-height: 100vh;
  width: 100%;
  padding: 3.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2.75rem;
  background:
    radial-gradient(circle at top, rgba(212, 175, 55, 0.08), transparent 36%),
    radial-gradient(circle at bottom right, rgba(255, 255, 255, 0.04), transparent 30%),
    linear-gradient(180deg, #081711 0%, #04100b 100%);
  overflow: hidden;
}

.hero-header {
  text-align: center;
  color: #fff;
  width: 100%;
  max-width: 820px;
  margin: 0 auto;
}

.eyebrow {
  display: inline-block;
  margin: 0 0 1rem;
  padding: 0.45rem 1rem;
  border-radius: 999px;
  background: rgba(212, 175, 55, 0.12);
  border: 1px solid rgba(212, 175, 55, 0.25);
  color: #d8b95a;
  font-size: 0.82rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}


.hero-text {
  margin: 1rem auto 0;
  max-width: 680px;
  font-size: 1.05rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.8);
}

.cards-grid {
  width: min(1200px, 100%);
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.5rem;
}

.split-card {
  position: relative;
  min-height: 540px;
  border-radius: 30px;
  overflow: hidden;
  text-decoration: none;
  display: flex;
  align-items: flex-end;
  padding: 2.5rem;
  box-shadow: 0 22px 55px rgba(0, 0, 0, 0.34);
  transform: translateY(0);
  transition: transform 0.35s ease, box-shadow 0.35s ease, filter 0.35s ease;
  isolation: isolate;
}

.split-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 28px 70px rgba(0, 0, 0, 0.45);
  filter: saturate(1.05);
}

.hospedaje-side {
  background-image: url('@/img/ancestral.jpg');
  background-size: cover;
  background-position: center;
}

.eventos-side {
  background-image: url('@/img/casa okfan.jpg');
  background-size: cover;
  background-position: center;
}

.overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(0, 0, 0, 0.02), rgba(0, 0, 0, 0.82)),
    linear-gradient(135deg, rgba(4, 16, 11, 0.42), rgba(212, 175, 55, 0.08));
  z-index: 0;
}

.split-card::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 30px;
  border: 1px solid rgba(212, 175, 55, 0.18);
  pointer-events: none;
}

.card-content {
  position: relative;
  z-index: 1;
  color: #fff;
  max-width: 440px;
}

.card-label {
  display: inline-block;
  margin-bottom: 0.9rem;
  padding: 0.36rem 0.9rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(12px);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.title {
  font-size: clamp(2rem, 4vw, 3.35rem);
  line-height: 1.05;
  margin: 0 0 0.75rem;
  font-weight: 800;
  text-shadow: 0 10px 28px rgba(0, 0, 0, 0.42);
}

.subtitle {
  font-size: 1.05rem;
  line-height: 1.7;
  margin-bottom: 1.7rem;
  color: rgba(255, 255, 255, 0.86);
  max-width: 34ch;
}

.btn-ingresar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.95rem 1.45rem;
  min-height: 48px;
  border-radius: 999px;
  background: linear-gradient(135deg, #d4af37, #b8912e);
  color: #081711;
  font-weight: 800;
  font-size: 0.98rem;
  letter-spacing: 0.02em;
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
  box-shadow: 0 10px 24px rgba(212, 175, 55, 0.22);
}

.split-card:hover .btn-ingresar {
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(212, 175, 55, 0.3);
}

@media (max-width: 900px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }

  .split-card {
    min-height: 390px;
    padding: 2rem;
  }

  .split-landing {
    padding: 2rem 1rem;
  }
}
</style>