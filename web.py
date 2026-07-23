from flask import Flask, render_template, request, redirect, url_for, jsonify
import bd
import os

loc_bd="data/itrm.db"
web = Flask(__name__)

tabelas1={
    "setor":"setores",
    "responsavel":"responsaveis",
    "ativo":"ativos",
    "vulnerabilidade":"vulnerabilidades"
}
tabelas2={
    "A":"ativos",
    "V":"vulnerabilidades",
    "S":"setores",
    "R":"responsaveis"
}
tabelas3={
    "ativos":"A",
    "vulnerabilidades":"V",
    "setores":"S",
    "responsaveis":"R"
}
@web.route("/")
def index():
    if not os.path.exists(loc_bd): bd.criar_tabelas()
    return render_template("index.html")

def conversor_lista(l,modo,tabela): #Converts lists/multiple results into into json
    dict_list=[]
    if modo==1:
        new_dict={
            "tipo":tabelas3[tabela],
            "id": l[0],
            "nome": l[1]
        }
        dict_list.append(new_dict)
    else:
        for x in l:
            new_dict={
                "tipo":tabelas3[tabela],
                "id": x[0],
                "nome": x[1]
            }
            dict_list.append(new_dict)
    return jsonify(dict_list)

def conversor_view(bruto, tipo): #Converts singles results into json
    new_dict = {}
    new_dict["nome"]=bruto[1]
    new_dict["id"]=bruto[0]
    new_dict["tabela"]=tipo
    if tipo=="ativos":
        new_dict["setor"] = bruto[2]
        new_dict["categoria"] = bruto[3]
        new_dict["responsavel"] = bruto[4]
    elif tipo=="vulnerabilidades":
        new_dict["severidade"] = bruto[2]
        new_dict["ativo"] = bruto[3]
        new_dict["status"] = bruto[4]
        new_dict["descricao"] = bruto[5]
    return jsonify(new_dict)

@web.route("/search", methods=["GET","POST"])
def pesquisa():
    if request.method=="GET":
        if not os.path.exists(loc_bd): bd.criar_tabelas()
        return render_template("search.html")
    else:
        cru=request.get_json()
        n=[]
        modo=0
        tabela=tabelas2[cru["table"]]
        if cru["mode"]=="id":
            n=bd.busca_id(tabela,int(cru["value"]))
            modo=1
        elif cru["mode"]=="name":
            n=bd.busca_nome(tabela,cru["value"])
        elif cru["mode"]=="association":
            n=bd.busca_asso(tabela,int(cru["value"]))
        elif cru["mode"]=="table":
            n=bd.busca_lista(tabela)
        if cru["mode"]=="association" and tabela=="vulnerabilidades": tabela="ativos"
        elif cru["mode"]=="association" and tabela=="ativos": tabela="vulnerabilidades"
        elif cru["mode"]=="association" and tabela=="setores": tabela="ativos"
        elif cru["mode"]=="association" and tabela=="responsaveis": tabela="ativos"
        return conversor_lista(n,modo,tabela)

@web.route("/new", methods=["GET","POST"])
def add():
    if not os.path.exists(loc_bd): bd.criar_tabelas()
    if request.method=="GET": return render_template("novo.html")
    elif request.method=="POST":
        cru = dict(request.form)
        dados={}
        dados["tabela"]=tabelas1[cru["tipo"]]
        dados["nome"]=cru["nome"]
        if cru["tipo"]=="ativo":
            dados["setor"]=int(cru["id_setor"])
            dados["categoria"]=int(cru["categoria"])
            dados["responsavel"]=int(cru["id_responsavel"])
        elif cru["tipo"]=="vulnerabilidade":
            dados["severidade"]=int(cru["severidade"])
            dados["ativo"]=int(cru["id_ativo"])
            dados["status"]=cru["status"]
            dados["descricao"]=cru["descricao"]
        try:
            lastid=bd.add(dados)
            tabela=dados["tabela"]
            returnm=f"Cadastrado novo objeto na tabela {tabela} com ID={lastid}"
            return render_template("novo.html",mensagem=returnm)
        except Exception as erro:
            return erro
        
@web.route("/view", methods=["GET","PUT","DELETE"])
def view():
    if not os.path.exists(loc_bd): bd.criar_tabelas()
    if request.method=="GET":
        return render_template("view.html")
    elif request.method=="PUT":
        dados=request.get_json()
        resp=bd.atualizar(dados)
        if resp==0:
            return jsonify({
                "sucesso": True,
                "mensagem": "Objeto atualizado com sucesso."
            }), 200
        else:
            return jsonify({
                "sucesso": False,
                "mensagem": "Houve um erro ao atualizar o objeto."
            }), 500
    elif request.method=="DELETE":
        dados=request.get_json()
        deps=bd.cont_dep(dados["tabela"],dados["id"])
        resp=bd.deletar(dados["tabela"],dados["id"],deps)
        if resp==0:
            return jsonify({
                "sucesso": True,
                "mensagem": "Objeto removido com sucesso."
            }), 200
        else:
            return jsonify({
                "sucesso": False,
                "mensagem": "Houve um erro ao deletar o objeto."
            }), 500

@web.route("/api/view")
def api_view():
    tabela = tabelas2[request.args["t"]]
    id = int(request.args["id"])
    objeto = bd.busca_id(tabela, id)
    return conversor_view(objeto,tabela)

os.makedirs("data", exist_ok=True)

if __name__ == "__main__":
    web.run(debug=True)
