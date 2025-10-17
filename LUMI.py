import streamlit as st
from google import genai
from google.genai import types

# 1. CONFIGURACIÓN DE LA CLAVE DE API
# ¡CRÍTICO! Pega la clave larga REAL aquí
# Tu clave debe empezar con AIzaSy... (NO es el nombre de la clave)
API_KEY = st.secrets["API_KEY"]

# 2. EL SYSTEM PROMPT MEJORADO (La Identidad de Lumi)
SYSTEM_PROMPT = (
    "Eres un asistente experto en análisis, generación y conversación de texto llamado **'Lumi'**. "
    "Tu función principal es ayudar con resúmenes, preguntas y respuestas, pero también estás "
    "diseñado para ser amigable y capaz de entablar una conversación casual. Responde a saludos "
    "y preguntas sobre tu 'estado' de forma optimista y profesional, recordando que eres una IA. "
    "Estrictamente prohibido generar o mencionar imágenes, videos o cualquier otro formato que no sea texto plano."
)

# --- Funciones de Inicialización ---

@st.cache_resource
def iniciar_cliente():
    """Inicializa y almacena el cliente de Gemini."""
    try:
        return genai.Client(api_key=API_KEY)
    except Exception as e:
        st.error(f"Error al inicializar el cliente: Verifica la clave API. {e}")
        return None

@st.cache_resource
def iniciar_sesion_chat(_cliente): # <-- SOLUCIÓN al error 'UnhashableParamError'
    """Inicializa la sesión de chat con el System Prompt."""
    
    if not _cliente: # Usa el guion bajo aquí también
        return None
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT
    )
    # Crea y devuelve el objeto Chat usando el cliente
    return _cliente.chats.create(
        model='gemini-2.5-flash',
        config=config
    )

# --- Lógica de la Aplicación Streamlit ---

if __name__ == "__main__":
    
    # 1. Título y Configuración de la Aplicación
    st.title("🤖 Asistente Conversacional Lumi (Web)")
    st.markdown("---")

    # 2. Inicialización del Cliente y Sesión
    cliente = iniciar_cliente()
    chat = iniciar_sesion_chat(cliente) # Le pasamos el cliente para que lo cachee

    if not chat:
        st.stop() # Detiene la ejecución si hay un error en la API Key

    # 3. Inicializar el Historial de la Sesión de Streamlit
    if "messages" not in st.session_state:
        # Crea una lista vacía para almacenar los mensajes
        st.session_state.messages = []

    # 4. Mostrar el Historial de Mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 5. Entrada de Usuario (El Cuadro de Chat)
    if prompt := st.chat_input("Escribe tu pregunta o saludo aquí..."):
        
        # a. Muestra el mensaje del usuario y lo añade al historial
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # b. Envía el mensaje a la sesión de chat (mantiene el contexto)
        try:
            response = chat.send_message(prompt)
            
            # c. Muestra la respuesta de Lumi y la añade al historial
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            error_message = f"Lumi: Disculpa, hubo un error al procesar tu solicitud. Error: {e}"
            with st.chat_message("assistant"):
                 st.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})