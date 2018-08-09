from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register",views.register_view, name="register"),
    path("updatetask", views.updatetask, name="updatetask"),
    path("deletetask", views.deletetask, name="deletetask"),
    path("movetask", views.movetask, name="movetask"),
    path("createtask", views.createtask, name="createtask"),
    path("createproject", views.createproject, name="createproject"),
    path("<int:projectid>/project", views.project, name="project"),

    #path("", views.index, name="index"),
    # path("updateorder/", views.updateorder, name="updateorder"),
    # path("<int:parentItemID>/removeitem", views.removeitem, name="removeitem"),
    # path("<int:order_id>/checkout", views.checkout, name="checkout"),
    # path("<int:order_id>/orderconfirm", views.orderconfirm, name="orderconfirm")
]
