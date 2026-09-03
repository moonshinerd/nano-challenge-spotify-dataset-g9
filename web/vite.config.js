import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Por padrão o Vite só aceita requisições com Host localhost/IP direto
    // (proteção contra DNS rebinding). Como acessamos por um domínio
    // próprio (via Cloudflare Tunnel), precisa liberar explicitamente.
    allowedHosts: ['music.schmidt.monster'],
    // O front chama a API por caminho relativo (ex: /search), e o Vite
    // encaminha pro container da API (rede interna do Docker, resolve
    // "api" pelo DNS do compose). Assim o navegador só precisa falar com
    // UMA porta (5173) — antes, acessando de outro dispositivo na rede
    // (ex: celular), a porta 8000 às vezes ficava inacessível mesmo com
    // 5173 funcionando normalmente (provável bloqueio/reserva de porta no
    // roteador da rede, fora do nosso controle). Com o proxy, isso deixa
    // de importar: só a 5173 precisa estar aberta.
    proxy: {
      '/search': { target: 'http://api:8000', changeOrigin: true },
      '/recommend': { target: 'http://api:8000', changeOrigin: true },
      '/recommend_playlist': { target: 'http://api:8000', changeOrigin: true },
      '/play': { target: 'http://api:8000', changeOrigin: true },
      '/thumbnail': { target: 'http://api:8000', changeOrigin: true },
    },
  },
})
