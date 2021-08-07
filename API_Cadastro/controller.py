from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Pessoa, Tokens
from secrets import token_hex
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from hashlib import sha256
import datetime


def conectaBanco():
    engine = create_engine('sqlite:///sqlite.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/cadastro')
def cadastro(user: str, email: str, senha: str):

    '''
        Descrição:
            Função responsável por efetuar o cadastro do usuário no banco de dados

        Parâmetros:
            usuario:
                Nome do usuário a ser cadastrado
            email:
                Email a ser cadastrado
            senha:
                Senha a ser cadastrada
        
        Retornos:
            0:
                Cadastro realizado com sucesso
            1:
                Senha com menos de 6 dígitos
            2:
                Usuário já cadastrado no sistema
            3: 
                Erro ao inserir na tabela
    '''

    if len(senha) < 6:
        return {'erro': 1}
    
    senha = sha256(senha.encode()).hexdigest()
    session = conectaBanco()
    usuario = session.query(Pessoa).filter_by(email = email).all()

    if len(usuario) > 0:
        return {'erro': 2}

    try:
        novo_usuario = Pessoa(
                                usuario=user,
                                email=email,
                                senha=senha
                                )
        session.add(novo_usuario)
        session.commit()
        return {'erro': 0}
    except Exception as e:
        return {'erro': 3, 'erro': e}

@app.post('/login')
def login(user: str, senha: str):
    senha = sha256(senha.encode()).hexdigest()
    
    session = conectaBanco()
    usuario = session.query(Pessoa).filter_by(usuario=user, senha=senha).all()

    if len(usuario) >= 1:
        hash = token_hex(50)
        existeHash = session.query(Tokens).filter_by(token=hash).all()
        while len(existeHash) > 1:
            hash = token_hex(50)
            existeHash = session.query(Tokens).filter_by(token=hash).all()
        
        usuarioExiste = session.query(Tokens).filter_by(id_pessoa=usuario[0].id).all()
        if len(usuarioExiste) > 0:
            usuarioExiste[0].token = hash
            usuarioExiste[0].data = datetime.datetime.now()
            
        elif len(usuarioExiste) == 0:
            novoToken = Tokens(id_pessoa=usuario[0].id, token=hash)
            session.add(novoToken)
        
        session.commit()
        return {'logado': hash}
    else:
        return {'logado': 'Usuário ou senha inexistentes'}


if __name__ == '__main__':
    uvicorn.run('controller:app', port=5000, reload=True, access_log=False)