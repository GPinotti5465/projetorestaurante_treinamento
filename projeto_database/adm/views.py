# NÃO ESQUECE DE FAZER ITERAÇÃO NO NÚMERO DE COLUNAS DA TABELA PEDIDOS PRO FETCHALL FUNCIONAR!
from django.shortcuts import render
import mysql.connector as mysql
import json
from datetime import datetime
import pandas as pd


# -------------------------DEFINIÇÃO LISTA DE PRODUTOS/PREÇOS, NÚMERO DO PEDIDO ATUAL E QUANTIDADE DE MESAS LIVRES
def index(request):
    conn = mysql.connect(
        host="localhost",
        database="databasecienciae_001",
        user="cienciae",
        password="ciencia#2023"
    )


    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mesas")
    num_mesas = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM produtos")
    prodbruto = cursor.fetchall()

    
    fetchprodutos = [t[0] for t in prodbruto]
    fetchprecos = [t[1] for t in prodbruto]

    cursor.execute("SELECT * FROM pedidos")
    registros = cursor.fetchall()
    temppedidoatual = len(registros)


    print(prodbruto)
    listaprodutos = json.dumps(fetchprodutos)
    listaprecos = json.dumps(fetchprecos)



# ---------------------------------------------REDIRECIONAMENTO POST NULO OU ERRO DE PREENCHIMENTO
    if request.method != "POST":
        return render(request, 'main.html', {"error": 0, "listaprodutos": listaprodutos, "listaprecos": listaprecos, "livres": num_mesas})
    if request.POST["nomecliente"] == "" or request.POST["reservmesa"] == "" or int(request.POST["counteritens"]) == 0:
        return render(request, 'main.html', {"error": 1, "listaprodutos": listaprodutos, "listaprecos": listaprecos, "livres": num_mesas})
 

# ----------------------------------------------------DEFINIÇÃO DE VARIÁVEIS BÁSICAS
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")
    numeropedido = temppedidoatual # "5"
    nomecliente = request.POST["nomecliente"] # "Nome"
    reservmesa = request.POST["reservmesa"] # "4" (não relevante)
    quantitens = int(request.POST["counteritens"]) # "2"
    totalpedido = request.POST["totalpedido"] # "15"
    ptemp = request.POST["listprodutos"]
    ptemp = ptemp.split("@")
    produtos = ptemp[:-1] # ["X-salada", "milkshake"]
    request.POST=None
    request._load_post_and_files()


# ----------------------------------------------------ITERAÇÃO LISTA DE QUANTIDADE
    listqtt = [] # ["3", "2", "1"]
    c=1
    while c<= quantitens:
        listqtt += request.POST[f"qttitem{c}"]
        c+=1
    if len(listqtt) != quantitens:
        return render(request, 'main.html', {"error": 1, "listaprodutos": listaprodutos, "listaprecos": listaprecos, "livres": num_mesas})



# --------------------------------------------------------ORGANIZAÇÃO LISTA DE PREÇOS (PAREAMENTO COM LISTA DE PRODUTOS)
    conn = mysql.connect(
    host="localhost",
    database="databasecienciae_001",
    user="cienciae",
    password="ciencia#2023"
    )

    placeholders = ','.join(['%s']*len(produtos))

    # connect to the database and execute the SQL query
    cursor = conn.cursor()
    query = f"SELECT precoproduto FROM produtos WHERE nomeproduto IN ({placeholders}) ORDER BY CASE nomeproduto {' '.join([f'WHEN %s THEN {i+1}' for i in range(len(produtos))])} END"
    cursor.execute(query, produtos+produtos)
    results = cursor.fetchall()
    # convert the results to a list of prices
    price_list = [result[0] for result in results]

    # close the database connection





# ----------------------------------------------------INPUT FINAL
    conn = mysql.connect(
    host="localhost",
    database="databasecienciae_001",
    user="cienciae",
    password="ciencia#2023"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE nomecliente = %s", (nomecliente,))
    existing_customer = cursor.fetchone()
    if not existing_customer:
        cursor.execute(f"INSERT INTO clientes (nomecliente) VALUES ('{nomecliente}')")
        conn.commit()

    temppedidonum = (numeropedido+1)
    temppedidomesa = reservmesa
    temppedidocliente = nomecliente
    temppedidodatah = f"{data} - {hora}"
    temppedidototal = totalpedido
    cursor.execute(f"INSERT INTO pedidos (numeropedido, numeromesa, nomecliente, dataif, total) VALUES ('{temppedidonum}', '{temppedidomesa}', '{temppedidocliente}', '{temppedidodatah}', '{temppedidototal}')")
    conn.commit()


    c=0
    while c < quantitens:
        cursor.execute(f"INSERT INTO itenspedido (numpedido, nomeproduto, quantidadeitem, valorunit, totalpedido) VALUES ('{numeropedido+1}', '{produtos[c]}', '{listqtt[c]}', '{price_list[c]}', '{str(int(listqtt[c]) * int(price_list[c]))}')")
        conn.commit()
        c+=1

    conn.close()


    return render(request, 'main.html', {"error": 0, "listaprodutos": listaprodutos, "listaprecos": listaprecos, "livres": num_mesas})



def cadclient(request):

    conn = mysql.connect(
    host="localhost",
    database="databasecienciae_001",
    user="cienciae",
    password="ciencia#2023"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT nomecliente FROM clientes")


    rows = cursor.fetchall()

    conn.close()
    clientes_list = [row[0] for row in rows]

    df = pd.DataFrame({'Clientes': clientes_list})
    
    df = df.sort_values(by='Clientes')

    global finaltable
    finaltable = df.to_html(classes='table', index=False)

    # ---------------- formatação para rodapé e cabeçalho -------------------

    from datetime import datetime
    time = datetime.now()
    data = time.strftime("%d-%m-%Y")
    hora = time.strftime("%H:%M:%S")


    return render(request,'cadastrocliente.html', {"table": finaltable, "data": data, "hora": hora})

def cadprod(request):
    conn = mysql.connect(
    host="localhost",
    database="databasecienciae_001",
    user="cienciae",
    password="ciencia#2023"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT nomeproduto, precoproduto FROM produtos")

    # Fetch all values as a list of tuples
    rows = cursor.fetchall()
    conn.close()
    # Convert the list of tuples to two lists, one for each column
    relatprod = [row[0] for row in rows]
    relatpreco = [f"{row[1]:.2f}" for row in rows]



    df = pd.DataFrame({'Nome': relatprod, 'Preço': relatpreco})
    
    df = df.sort_values(by='Nome')

    global finaltable
    finaltable = df.to_html(classes='table', index=False)

    # ---------------- formatação para rodapé e cabeçalho -------------------

    from datetime import datetime
    time = datetime.now()
    data = time.strftime("%d-%m-%Y")
    hora = time.strftime("%H:%M:%S")


    return render(request,'cadastroprodutos.html', {"table": finaltable, "data": data, "hora": hora})


def relatpedido(request):
    conn = mysql.connect(
    host="localhost",
    database="databasecienciae_001",
    user="cienciae",
    password="ciencia#2023"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT numeropedido, numeromesa, nomecliente, dataif, total FROM pedidos")

    # Fetch all values as a list of tuples
    rows = cursor.fetchall()
    conn.close()
    # Convert the list of tuples to two lists, one for each column
    relatnum = [row[0] for row in rows]
    relatmesa = [row[1] for row in rows]
    relatclien = [row[2] for row in rows]
    relatdata = [row[3] for row in rows]
    relattotal = [f"{row[4]:.2f}" for row in rows]



    df = pd.DataFrame({'Núm. pedido': relatnum, 'Mesa': relatmesa, 'Cliente': relatclien, 'Data': relatdata, 'Total': relattotal})
    
    df = df.sort_values(by='Núm. pedido')

    global finaltable
    finaltable = df.to_html(classes='table', index=False)

    # ---------------- formatação para rodapé e cabeçalho -------------------

    from datetime import datetime
    time = datetime.now()
    data = time.strftime("%d-%m-%Y")
    hora = time.strftime("%H:%M:%S")


    return render(request,'relatpedidos.html', {"table": finaltable, "data": data, "hora": hora})


def extratopedido(request):
    if request.method != "POST":
        conn = mysql.connect(
        host="localhost",
        database="databasecienciae_001",
        user="cienciae",
        password="ciencia#2023"
        )
        cursor = conn.cursor()
        cursor.execute("select * from pedidos")
        registros = cursor.fetchall()
        temppedidoatual = len(registros)

        return render(request, 'extratoselect.html', {"maximo": temppedidoatual})
    pedidoselecionado = request.POST["pedidoselecionado"]
    request.POST=None
    request._load_post_and_files()
    conn = mysql.connect(
    host="localhost",
    database="databasecienciae_001",
    user="cienciae",
    password="ciencia#2023"
    )
    cursor = conn.cursor()

    cursor.execute(f"SELECT numpedido, nomeproduto, quantidadeitem, valorunit, totalpedido FROM itenspedido WHERE numpedido = '{pedidoselecionado}'")

    # Fetch all values as a list of tuples
    rows = cursor.fetchall()
    
    # Convert the list of tuples to two lists, one for each column
    relatnum = [row[0] for row in rows]
    relatprod = [row[1] for row in rows]
    relatquant = [row[2] for row in rows]
    relatunit = [row[3] + "0" for row in rows]
    relattotal = [row[4] + ".00" for row in rows]

    cursor.execute(f"SELECT dataif FROM pedidos WHERE numeropedido = '{pedidoselecionado}'")
    datahpedido = str(cursor.fetchall())
    datahpedido = datahpedido[3:-4]
    conn.close()
    df = pd.DataFrame({'Produto': relatprod, 'Quantidade': relatquant, 'Valor unit.': relatunit, 'Total': relattotal})
    
    df = df.sort_values(by='Produto')

    global finaltable
    finaltable = df.to_html(classes='table', index=False)

    # ---------------- formatação para rodapé e cabeçalho -------------------

    from datetime import datetime
    time = datetime.now()
    data = time.strftime("%d-%m-%Y")
    hora = time.strftime("%H:%M:%S")


    return render(request,'relatextrato.html', {"table": finaltable, "data": data, "hora": hora, "num": pedidoselecionado, "datah": datahpedido})


