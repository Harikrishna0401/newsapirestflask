from mvc import app
from .views import Showall,Createuser,Editdetails,Login,News,Category




app.add_url_rule('/showuser',view_func=Showall.as_view('Suser'))
app.add_url_rule('/signin',view_func=Createuser.as_view('user'))
app.add_url_rule('/user/<public_id>', view_func=Editdetails.as_view('Euser'))
app.add_url_rule('/login',view_func=Login.as_view('login'))
app.add_url_rule('/news',view_func=News.as_view('news'))
app.add_url_rule('/category',view_func=Category.as_view('category'))
