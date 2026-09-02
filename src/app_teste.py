import streamlit as st
from ytmusicapi import YTMusic

st.set_page_config(page_title="Teste YT Music API", layout="centered")

st.title("🎵 Teste: YouTube Music API")
st.write("Pesquise uma música para testar se a API `ytmusicapi` retorna a capa e o link corretamente (sem precisar de autenticação).")

@st.cache_resource
def get_yt_client():
    return YTMusic()

yt = get_yt_client()

query = st.text_input("Digite o nome da música e artista (ex: Sam Smith Unholy)")

if st.button("Buscar") and query:
    with st.spinner("Buscando no YouTube Music..."):
        try:
            # Faz a busca focada apenas em músicas
            results = yt.search(query, filter="songs", limit=3)
            
            if not results:
                st.warning("Nenhuma música encontrada.")
            else:
                st.success(f"Encontramos {len(results)} resultados para '{query}'!")
                
                for idx, track in enumerate(results):
                    st.subheader(f"{idx + 1}. {track['title']}")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Pega a melhor resolução da imagem da capa
                        if 'thumbnails' in track and track['thumbnails']:
                            img_url = track['thumbnails'][-1]['url']
                            st.image(img_url, width=150)
                        else:
                            st.write("Sem capa disponível.")
                            
                    with col2:
                        # Extrai artistas
                        artistas = ", ".join([a['name'] for a in track.get('artists', [])])
                        album = track.get('album', {}).get('name', 'Single/Desconhecido') if track.get('album') else 'Single/Desconhecido'
                        
                        st.write(f"**Artista(s):** {artistas}")
                        st.write(f"**Álbum:** {album}")
                        
                        # Monta o link clicável para ouvir
                        if 'videoId' in track and track['videoId']:
                            link = f"https://music.youtube.com/watch?v={track['videoId']}"
                            st.markdown(f"**[▶️ Ouvir no YT Music]({link})**")
                        else:
                            st.write("Link não disponível.")
                            
                    st.divider()
        except Exception as e:
            st.error(f"Ocorreu um erro ao buscar na API: {e}")
