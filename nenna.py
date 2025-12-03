import streamlit as st
import urllib.parse
import requests
import json
from datetime import datetime

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Nenna Pizzaria", page_icon="🍕", layout="centered")

# Dados da Loja
WHATSAPP_NUMBER = "5532988822076" 
CHAVE_PIX = "10787567671"  # CPF
NOME_BENEFICIARIO_PIX = "NENNA PIZZARIA"
CIDADE_PIX = "JUIZ DE FORA"

# --- FUNÇÕES ÚTEIS (Backend) ---

def buscar_endereco_por_cep(cep):
    """Busca endereço usando a API pública ViaCEP"""
    cep = cep.replace("-", "").replace(".", "").strip()
    if len(cep) == 8:
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            if response.status_code == 200:
                dados = response.json()
                if "erro" not in dados:
                    return dados
        except:
            pass
    return None

def gerar_payload_pix(chave, nome, cidade, valor):
    """
    Gera o código 'Copia e Cola' do PIX (Padrão EMV BR Code).
    O valor deve ser float (ex: 150.00).
    """
    valor_str = f"{valor:.2f}"
    
    # Montagem dos campos do PIX (IDs e tamanhos)
    payload = f"00020126360014BR.GOV.BCB.PIX0111{chave}52040000530398654{len(valor_str):02}{valor_str}5802BR59{len(nome):02}{nome}60{len(cidade):02}{cidade}62070503***6304"
    
    # Cálculo do CRC16 (Ciclic Redundancy Check)
    def crc16_ccitt(data):
        crc = 0xFFFF
        poly = 0x1021
        for char in data:
            byte = ord(char)
            crc ^= (byte << 8)
            for _ in range(8):
                if (crc & 0x8000):
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return f"{crc:04X}"

    crc_code = crc16_ccitt(payload)
    return payload + crc_code

# --- DADOS DO CARDÁPIO ---
# (Você pode expandir isso depois)
pizzas = {
    "Mussarela": 45.00, "Calabresa": 45.00, 
    "Portuguesa": 50.00, "Marguerita": 48.00,
    "Frango c/ Catupiry": 55.00, "Quatro Queijos": 58.00
}
bebidas = {
    "Coca-Cola 2L": 14.00, "Guaraná 2L": 12.00
}

# --- INTERFACE (Frontend) ---

st.image("https://img.freepik.com/fotos-gratis/fatia-de-pizza-crocante-de-carne-e-queijo_140725-6974.jpg", use_container_width=True)
st.title("🍕 Nenna Pizzaria - Pedido Digital")
st.markdown("**Faça seu pedido e finalize no WhatsApp num piscar de olhos!**")

# 1. Identificação do Cliente (Simulação de Cadastro)
st.info("👋 Já é cliente? Digite seu telefone para carregar seus dados.")
telefone_cliente = st.text_input("Seu Telefone (apenas números)", max_chars=11, help="Ex: 32999999999")

# Variáveis para preenchimento automático
nome_padrao = ""
cep_padrao = ""
endereco_padrao = ""

# Simulação de "Banco de Dados" (Isso depois virá do Google Sheets)
# Se o cliente digitar este número teste, os dados aparecem.
if telefone_cliente == "32999999999": 
    st.toast("Cliente encontrado! Carregando dados...", icon="🎉")
    nome_padrao = "Cliente Teste Nenna"
    cep_padrao = "36000000"
    endereco_padrao = "Rua Teste, 100 - Centro"

with st.expander("📝 Seus Dados", expanded=True):
    col_a, col_b = st.columns(2)
    nome = col_a.text_input("Nome Completo", value=nome_padrao)
    
    # Busca de Endereço Inteligente
    cep = col_b.text_input("CEP (apenas números)", value=cep_padrao, max_chars=8)
    
    endereco_completo = st.text_area("Endereço e Número", value=endereco_padrao, placeholder="Rua das Flores, 123 - Apto 101")
    
    # Gatilho para buscar CEP se o usuário digitou e o campo de endereço está vazio
    if cep and len(cep) == 8 and not endereco_completo:
        dados_cep = buscar_endereco_por_cep(cep)
        if dados_cep:
            rua = dados_cep.get('logradouro', '')
            bairro = dados_cep.get('bairro', '')
            cidade = dados_cep.get('localidade', '')
            # Atualiza o estado da caixa de texto
            endereco_completo = f"{rua}, Nº... - {bairro}, {cidade}"
            st.success(f"Endereço localizado: {rua}")
            st.rerun() # Recarrega para preencher o campo

st.divider()

# 2. Escolha dos Itens
carrinho = []
total = 0.0

tab1, tab2 = st.tabs(["🍕 Pizzas", "🥤 Bebidas"])

with tab1:
    for sabor, preco in pizzas.items():
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{sabor}** (R$ {preco:.2f})")
        if c2.checkbox("Adicionar", key=f"add_{sabor}"):
            qtd = c3.number_input("Qtd", 1, 10, key=f"qtd_{sabor}", label_visibility="collapsed")
            total += preco * qtd
            carrinho.append(f"{qtd}x Pizza {sabor} (R$ {preco * qtd:.2f})")

with tab2:
    for item, preco in bebidas.items():
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{item}** (R$ {preco:.2f})")
        if c2.checkbox("Adicionar", key=f"add_{item}"):
            qtd = c3.number_input("Qtd", 1, 10, key=f"qtd_{item}", label_visibility="collapsed")
            total += preco * qtd
            carrinho.append(f"{qtd}x {item} (R$ {preco * qtd:.2f})")

st.divider()

# 3. Pagamento e Finalização
st.subheader(f"💰 Total: R$ {total:.2f}")

forma_pagamento = st.radio("Como deseja pagar?", ["PIX", "Cartão (Entregador)", "Dinheiro"])

pix_copia_cola = ""

if forma_pagamento == "PIX" and total > 0:
    st.info("Gerando código PIX...")
    pix_copia_cola = gerar_payload_pix(CHAVE_PIX, NOME_BENEFICIARIO_PIX, CIDADE_PIX, total)
    
    col_pix1, col_pix2 = st.columns([4, 1])
    col_pix1.text_input("Copia e Cola (Copie o código abaixo)", value=pix_copia_cola)
    st.caption(f"Chave CPF: {CHAVE_PIX} - {NOME_BENEFICIARIO_PIX}")
    st.warning("⚠️ Realize o pagamento e envie o comprovante no WhatsApp após finalizar o pedido.")

obs = st.text_input("Observações (Ex: troco para 50, sem cebola, campainha estragada)")

# Botão Final
if st.button("🚀 Enviar Pedido para WhatsApp", type="primary", use_container_width=True):
    if not nome or not endereco_completo or total == 0:
        st.error("Preencha nome, endereço e adicione itens ao carrinho!")
    else:
        # Criação da Mensagem
        msg = f"*PEDIDO NENNA PIZZARIA* 🍕\n"
        msg += f"--------------------------------\n"
        msg += f"👤 *Cliente:* {nome}\n"
        msg += f"📱 *Tel:* {telefone_cliente}\n"
        msg += f"📍 *Endereço:* {endereco_completo}\n"
        msg += f"--------------------------------\n"
        msg += "*ITENS:*\n" + "\n".join(carrinho)
        msg += f"\n--------------------------------\n"
        msg += f"💰 *TOTAL: R$ {total:.2f}*\n"
        msg += f"💳 *Pagamento:* {forma_pagamento}\n"
        if obs: msg += f"📝 *Obs:* {obs}\n"
        
        # Link do WhatsApp
        msg_encoded = urllib.parse.quote(msg)
        link_zap = f"https://wa.me/{WHATSAPP_NUMBER}?text={msg_encoded}"
        
        st.success("Tudo pronto! Clique no botão abaixo para abrir o WhatsApp.")
        st.link_button("📲 Confirmar no WhatsApp", link_zap)
