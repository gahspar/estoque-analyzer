import pandas as pd
import numpy as np

def analisar_planilha_detalhada(arquivo, nome):
    print(f"\n{'='*50}")
    print(f"ANÁLISE DETALHADA: {nome}")
    print(f"{'='*50}")
    
    try:
        # Ler sem header
        df = pd.read_excel(arquivo, header=None)
        print(f"Shape: {df.shape}")
        
        # Procurar por linhas com dados reais
        print("\nProcurando por linhas com dados...")
        for i in range(min(30, len(df))):
            linha = df.iloc[i]
            valores_nao_nulos = linha.dropna()
            
            if len(valores_nao_nulos) > 0:
                print(f"\nLinha {i}:")
                for j, valor in enumerate(linha):
                    if pd.notna(valor):
                        print(f"  Coluna {j}: {valor} (tipo: {type(valor)})")
                
                # Se parece ser uma linha de dados (tem código e descrição)
                if len(valores_nao_nulos) >= 2:
                    # Verificar se tem padrão de código (números)
                    tem_codigo = any(str(v).strip().isdigit() for v in valores_nao_nulos if str(v).strip())
                    # Verificar se tem descrição (texto longo)
                    tem_descricao = any(len(str(v).strip()) > 10 for v in valores_nao_nulos if str(v).strip())
                    
                    if tem_codigo or tem_descricao:
                        print(f"  *** POSSÍVEL LINHA DE DADOS ***")
                        print(f"  Tem código: {tem_codigo}")
                        print(f"  Tem descrição: {tem_descricao}")
                        
                        # Tentar identificar colunas
                        for j, valor in enumerate(linha):
                            if pd.notna(valor):
                                valor_str = str(valor).strip()
                                if valor_str.isdigit() and len(valor_str) >= 2:
                                    print(f"    Coluna {j} parece ser CÓDIGO: {valor}")
                                elif len(valor_str) > 10 and valor_str.replace(' ', '').isalpha():
                                    print(f"    Coluna {j} parece ser DESCRIÇÃO: {valor}")
                                elif valor_str.upper() in ['UN', 'AMP', 'COM', 'KG', 'L', 'ML']:
                                    print(f"    Coluna {j} parece ser UNIDADE: {valor}")
                                elif valor_str.replace('.', '').replace(',', '').isdigit():
                                    print(f"    Coluna {j} parece ser QUANTIDADE: {valor}")
        
        # Mostrar algumas linhas finais para ver se há padrão
        print(f"\nÚltimas 5 linhas:")
        print(df.tail())
        
    except Exception as e:
        print(f"Erro ao analisar {nome}: {e}")

if __name__ == "__main__":
    analisar_planilha_detalhada('Saldos de Estoque.xlsx', 'Saldos de Estoque')
    analisar_planilha_detalhada('Saídas de Insumos.xlsx', 'Saídas de Insumos') 