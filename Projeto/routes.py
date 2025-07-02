from flask import render_template, url_for, redirect
from Projeto import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from Projeto.models import Usuario, Categoria, Tarefa
from Projeto.forms import FormLogin, FormCriarConta, FormTarefa


@app.route("/", methods=["GET", "POST"])
def homepage():
    formLogin = FormLogin()
    if formLogin.validate_on_submit():
        usuario = Usuario.query.filter_by(email=formLogin.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, formLogin.senha.data):
            login_user(usuario)
        return redirect(url_for('perfil', id_usuario=usuario.id))
    return render_template('home.html', form=formLogin, usuario=current_user)


@app.route('/criar-conta', methods=["GET", "POST"])
def criarconta():
    formcriarconta = FormCriarConta()
    if formcriarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(formcriarconta.senha.data).decode('utf-8')
        usuario = Usuario(nome=formcriarconta.username.data, email=formcriarconta.email.data, senha=senha)

        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for('perfil', id_usuario=usuario.id))
    return render_template('criarconta.html', form=formcriarconta)


@app.route('/user/<username>')
def user_profile(username):
    usuario = Usuario.query.filter_by(nome=username).first_or_404()
    return redirect(url_for('perfil', id_usuario=usuario.id))



@app.route('/post/<int:post_id>')
def post_detail(post_id):
    return render_template('post.html', post_id=post_id)


@app.route('/Tarefa/<int:id_usuario>', methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    form = FormTarefa()

    # Carrega as categorias para o SelectField
    form.categoria.choices = [(c.id, c.nome) for c in Categoria.query.all()]

    # Processa o formulário de criação de tarefa
    if form.validate_on_submit():
        nova_tarefa = Tarefa(
            titulo=form.titulo.data,
            usuario_id=usuario.id,
            categoria_id=form.categoria.data
        )
        database.session.add(nova_tarefa)
        database.session.commit()
        return redirect(url_for('perfil', id_usuario=usuario.id))

    return render_template('user.html', usuario=usuario, form=form)

