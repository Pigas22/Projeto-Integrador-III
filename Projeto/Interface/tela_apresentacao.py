import streamlit as st  # type: ignore


def tela_apresentacao():
    st.markdown(
        """
        <div style='text-align: center; padding: 50px 20px;'>
            <h1 style='font-size: 42px;'>Análise de Acidentes de Trânsito no Brasil</h1>
            <h3>Período: 2021 a 2025</h3>
            <p style='font-size: 18px; max-width: 700px; margin: 20px auto; line-height: 1.5;'>
                Este projeto tem como objetivo analisar e visualizar dados sobre acidentes de trânsito no Brasil.
                Através de gráficos interativos, você poderá explorar os dados por estado, tipo de acidente, condições meteorológicas,
                sexo, horário e muito mais.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        /* Centraliza o container do botão */
        div.stButton {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }

        div.stButton > button {
            background-color: #007BFF;
            color: white;
            font-size: 20px;
            padding: 12px 30px;
            border-radius: 8px;
            border: none;
            transition: background-color 0.3s ease;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            font-weight: 600;
        }

        div.stButton > button:hover {
            background-color: #0056b3;
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🚦 Ir para a Análise"):
        st.session_state["pagina"] = "analise"
        st.rerun()
