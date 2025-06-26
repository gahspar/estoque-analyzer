import pandas as pd
import numpy as np

def analisar_planilha_estoque():
    print("=== ANALISANDO PLANILHA DE ESTOQUE ===")
    
    # Tentar diferentes formas de ler a planilha
    try:
        # Tentar ler sem header
        df = pd.read_excel('Saldos de Estoque.xlsx', header=None)
        print(f"Shape: {df.shape}")
        print("\nPrimeiras 15 linhas:")
        print(df.head(15))
        
        # Procurar por linhas com dados
        for i in range(min(20, len(df))):
            linha = df.iloc[i]
            if not linha.isna().all():
                print(f"\nLinha {i} (não vazia):")
                print(linha.tolist())
                
    except Exception as e:
        print(f"Erro: {e}")

def analisar_planilha_saidas():
    print("\n=== ANALISANDO PLANILHA DE SAÍDAS ===")
    
    try:
        # Tentar ler sem header
        df = pd.read_excel('Saídas de Insumos.xlsx', header=None)
        print(f"Shape: {df.shape}")
        print("\nPrimeiras 15 linhas:")
        print(df.head(15))
        
        # Procurar por linhas com dados
        for i in range(min(20, len(df))):
            linha = df.iloc[i]
            if not linha.isna().all():
                print(f"\nLinha {i} (não vazia):")
                print(linha.tolist())
                
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    analisar_planilha_estoque()
    analisar_planilha_saidas() 