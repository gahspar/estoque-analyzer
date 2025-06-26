#!/usr/bin/env python3
"""
Script principal para executar a aplicação de análise de estoque.
"""

import subprocess
import sys
import os
from pathlib import Path

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas."""
    try:
        import streamlit
        import pandas
        import openpyxl
        import xlsxwriter
        import numpy
        print("✅ Todas as dependências estão instaladas!")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def criar_exemplos():
    """Cria planilhas de exemplo se solicitado."""
    resposta = input("📊 Deseja criar planilhas de exemplo? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        try:
            from exemplos.estoque_exemplo import criar_planilhas_exemplo
            criar_planilhas_exemplo()
            print("\n🎉 Planilhas de exemplo criadas! Use-as para testar a aplicação.")
        except Exception as e:
            print(f"❌ Erro ao criar exemplos: {e}")

def executar_aplicacao():
    """Executa a aplicação Streamlit."""
    try:
        print("🚀 Iniciando aplicação de análise de estoque...")
        print("🌐 A aplicação será aberta em: http://localhost:8501")
        print("⏹️  Pressione Ctrl+C para parar a aplicação")
        print("-" * 50)
        
        # Executar Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário.")
    except Exception as e:
        print(f"❌ Erro ao executar aplicação: {e}")

def main():
    """Função principal."""
    print("📊 Análise de Estoque - Sistema de Gestão")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path("app.py").exists():
        print("❌ Arquivo app.py não encontrado!")
        print("💡 Certifique-se de estar no diretório correto do projeto.")
        return
    
    # Verificar dependências
    if not verificar_dependencias():
        return
    
    # Perguntar sobre exemplos
    criar_exemplos()
    
    print("\n" + "=" * 50)
    
    # Executar aplicação
    executar_aplicacao()

if __name__ == "__main__":
    main() 