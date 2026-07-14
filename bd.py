import sqlite3
nome_banco="data/itrm.db"
def conectar(): #Opens connection to database
    return sqlite3.connect(nome_banco)
def criar_tabelas(): #Creates tables if inexistent
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS responsaveis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);""")
    cursor.execute("""                
CREATE TABLE IF NOT EXISTS setores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);""")
    cursor.execute("""      
CREATE TABLE IF NOT EXISTS ativos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    setor INTEGER,
    categoria INTEGER,
    responsavel INTEGER,
    FOREIGN KEY(setor) REFERENCES setores(id)
        ON DELETE CASCADE,
    FOREIGN KEY(responsavel) REFERENCES responsaveis(id)
        ON DELETE CASCADE
);""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS vulnerabilidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    severidade INTEGER,
    ativo INTEGER NOT NULL,
    status TEXT DEFAULT 'Em Aberto.',
    descricao TEXT DEFAULT 'Sem descricao.',
    FOREIGN KEY(ativo) REFERENCES ativos(id)
        ON DELETE CASCADE
);""")
    conexao.commit()
    conexao.close()
def add(dados): #Adds new entries to tables 
    conexao = conectar()
    cursor = conexao.cursor()
    t=dados['tabela']
    if t=="ativos": cursor.execute("""INSERT INTO ativos (nome, setor, categoria, responsavel) VALUES (?, ?, ?, ?)""", (dados['nome'], dados['setor'], dados['categoria'], dados['responsavel'],))
    elif t=="vulnerabilidades": cursor.execute("INSERT INTO vulnerabilidades (nome,severidade,ativo,descricao,status) VALUES (?,?,?,?,?)", (dados['nome'], dados['severidade'], dados['ativo'], dados['descricao'], dados['status'],))
    elif t=="responsaveis": cursor.execute("INSERT INTO responsaveis (nome) VALUES (?)",(dados['nome'],))
    elif t=="setores": cursor.execute("INSERT INTO setores (nome) VALUES (?)",(dados['nome'],))
    conexao.commit()
    lastid=cursor.lastrowid
    conexao.close()
    return lastid
def deletar(tabela,id,deps): #Deletes an entry + dependencies from its table
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        if len(deps)>0:
            for x in deps:
                cursor.execute(f"DELETE FROM {x[1]} WHERE id = ?",(x[0],))
        cursor.execute(f"DELETE FROM {tabela} WHERE id = ?",(id,))
        conexao.commit()
        conexao.close()
        return 0
    except: return 1
def busca_lista(tabela): #Returns a list from all entries in a table
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(f"SELECT * FROM {tabela}")
    r = cursor.fetchall()
    conexao.close()
    return r
def busca_id(tabela,a): #Returns an entity based on ID and table
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(f"SELECT * FROM {tabela} WHERE id = ?", (a,))
    r = cursor.fetchone()
    conexao.close()
    return r
def cont_dep(tabela,id): #Returns a list of entities linked to another based on ID and table
    conexao = conectar()
    cursor = conexao.cursor()
    g=[]
    if tabela=="ativos":
        cursor.execute(f"SELECT * FROM vulnerabilidades WHERE ativo = ?",(id,))
        deps = cursor.fetchall()
        for x in deps:
            gg=(x[0],"vulnerabilidades")
            g.append(gg)
    elif tabela=="setores":
        cursor.execute(f"SELECT * FROM ativos WHERE setor = ?",(id,))
        deps = cursor.fetchall()
        for x in deps:
            cursor.execute(f"SELECT * FROM vulnerabilidades WHERE ativo = ?",(x[0],))
            vdeps=cursor.fetchall()
            for y in vdeps:
                ggg=(y[0],"vulnerabilidades")
                g.append(ggg)
            gg=(x[0],"ativos")
            g.append(gg)
    elif tabela=="responsaveis":
        cursor.execute(f"SELECT * FROM ativos WHERE responsavel = ?",(id,))
        deps = cursor.fetchall()
        for x in deps:
            cursor.execute(f"SELECT * FROM vulnerabilidades WHERE ativo = ?",(x[0],))
            vdeps=cursor.fetchall()
            for y in vdeps:
                ggg=(y[0],"vulnerabilidades")
                g.append(ggg)
            gg=(x[0],"ativos")
            g.append(gg)
    conexao.close()
    return g
def atualizar(dados): #Updates data of an entity
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        tabela = dados['tabela']
        if tabela=='ativos': cursor.execute(f"UPDATE ativos SET nome = ?, setor = ?, categoria = ?, responsavel = ? WHERE id = ?",(dados['nome'],dados['setor'],dados['categoria'],dados['responsavel'],dados['id']))
        elif tabela=='vulnerabilidades': cursor.execute(f"UPDATE vulnerabilidades SET nome = ?, severidade = ?, ativo = ?, status = ?, descricao = ? WHERE id = ?",(dados['nome'],dados['severidade'],dados['ativo'],dados['status'], dados['descricao'],dados['id']))
        elif tabela=='setores' or tabela=='responsaveis': cursor.execute(f"UPDATE {tabela} SET nome = ? WHERE id = ?",(dados['nome'],dados['id']))
        conexao.commit()
        conexao.close()
        return 0
    except: return 1
def busca_nome(tabela,termo): #Fetches entries by name
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(f"SELECT * FROM {tabela} WHERE nome LIKE ?",(f"%{termo}%",)) #Like search
    r = cursor.fetchall()
    conexao.close()
    return r
comandos={
    "ativos":"SELECT * FROM vulnerabilidades WHERE ativo = ?",
    "vulnerabilidades":"SELECT * FROM ativos WHERE id",
    "responsaveis":"SELECT * FROM ativos WHERE responsavel = ?",
    "setores":"SELECT * FROM ativos WHERE setor = ?"
}
def busca_asso(tabela,termo): #Fetches entries by association
    conexao = conectar()
    cursor = conexao.cursor()
    if tabela=="vulnerabilidades":
        f=busca_id("vulnerabilidades",termo)
        target_id=f[3]
        cursor.execute("SELECT * FROM ativos WHERE id = ?",(target_id,))
    else: cursor.execute(comandos[tabela],(termo,)) 
    r = cursor.fetchall()
    conexao.close()
    return r