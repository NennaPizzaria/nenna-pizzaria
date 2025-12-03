import streamlit as st
import urllib.parse

# --- Configurações Iniciais ---
st.set_page_config(page_title="Nenna Pizzaria", page_icon="🍕", layout="centered")

# Seu número de WhatsApp (com DDI e DDD)
WHATSAPP_NUMBER = "5532999999999"  # Substitua pelo seu número real

# --- Dados do Cardápio ---
pizzas = {
    "Mussarela": 45.00,
    "Calabresa": 45.00,
    "Portuguesa": 50.00,
    "Marguerita": 48.00,
    "Frango c/ Catupiry": 55.00
}

bebidas = {
    "Coca-Cola 2L": 14.00,
    "Guaraná 2L": 12.00,
    "Suco Del Valle": 10.00
}

# --- Interface do Usuário ---
st.image("https://img.freepik.com/fotos-gratis/fatia-de-pizza-crocante-de-carne-e-queijo_140725-6974.jpg", use_container_width=True) # Imagem ilustrativa
st.title("🍕 Nenna Pizzaria")
st.write("Selecione seus itens e envie o pedido direto no nosso WhatsApp!")

st.divider()

# Carrinho de Compras (Dicionário para armazenar quantidades)
carrinho_pizzas = {}
carrinho_bebidas = {}

# Seção de Pizzas
st.subheader("🍕 Pizzas")
for sabor, preco in pizzas.items():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.write(f"**{sabor}**")
        st.caption(f"R$ {preco:.2f}")
    with col2:
        # Checkbox para ativar o item
        if st.checkbox("Pedir", key=f"chk_{sabor}"):
            with col3:
                # Se ativado, mostra seletor de quantidade
                qtd = st.number_input("Qtd", min_value=1, value=1, key=f"qtd_{sabor}", label_visibility="collapsed")
                carrinho_pizzas[sabor] = (qtd, preco)

st.divider()

# Seção de Bebidas
st.subheader("🥤 Bebidas")
for item, preco in bebidas.items():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.write(f"**{item}**")
        st.caption(f"R$ {preco:.2f}")
    with col2:
        if st.checkbox("Pedir", key=f"chk_{item}"):
            with col3:
                qtd = st.number_input("Qtd", min_value=1, value=1, key=f"qtd_{item}", label_visibility="collapsed")
                carrinho_bebidas[item] = (qtd, preco)

st.divider()

# --- Finalização ---
st.subheader("📍 Dados de Entrega")
nome = st.text_input("Seu Nome")
endereco = st.text_area("Endereço Completo (Rua, Número, Bairro)")
pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Cartão Crédito", "Cartão Débito", "Dinheiro (Precisa de troco?)"])
obs = st.text_input("Observações (Ex: tirar cebola)")

# Cálculo do Total
total = 0
resumo_pedido = []

for item, (qtd, preco) in carrinho_pizzas.items():
    subtotal = qtd * preco
    total += subtotal
    resumo_pedido.append(f"🍕 {qtd}x {item} (R$ {subtotal:.2f})")

for item, (qtd, preco) in carrinho_bebidas.items():
    subtotal = qtd * preco
    total += subtotal
    resumo_pedido.append(f"🥤 {qtd}x {item} (R$ {subtotal:.2f})")

# Botão de Enviar
if st.button("✅ Finalizar Pedido", type="primary", use_container_width=True):
    if not nome or not endereco or total == 0:
        st.error("Por favor, preencha seu nome, endereço e selecione pelo menos um item.")
    else:
        # Montar a mensagem do WhatsApp
        msg = f"*NOVO PEDIDO - NENNA PIZZARIA*\n"
        msg += f"👤 *Cliente:* {nome}\n"
        msg += f"📍 *Endereço:* {endereco}\n"
        msg += f"--------------------------------\n"
        msg += "\n".join(resumo_pedido)
        msg += f"\n--------------------------------\n"
        msg += f"💰 *TOTAL: R$ {total:.2f}*\n"
        msg += f"💳 *Pagamento:* {pagamento}\n"
        msg += f"📝 *Obs:* {obs}"

        # Codificar mensagem para URL (transforma espaços em %20, etc)
        msg_encoded = urllib.parse.quote(msg)
        
        # Criar Link
        link_whatsapp = f"https://wa.me/{WHATSAPP_NUMBER}?text={msg_encoded}"
        
        # Mostrar botão final ou redirecionar
        st.success("Pedido Montado! Clique abaixo para enviar no WhatsApp:")
        st.link_button("📲 ENVIAR AGORA NO WHATSAPP", link_whatsapp, type="secondary")