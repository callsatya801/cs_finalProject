from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("", views.index, name="home"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("updatetask", views.updatetask, name="updatetask"),
    path("createtask", views.createtask, name="createtask"),
    path("<int:projectid>/project", views.project, name="project"),

    # path("updateorder/", views.updateorder, name="updateorder"),
    # path("<int:parentItemID>/removeitem", views.removeitem, name="removeitem"),
    # path("<int:order_id>/checkout", views.checkout, name="checkout"),
    # path("<int:order_id>/orderconfirm", views.orderconfirm, name="orderconfirm")
]
