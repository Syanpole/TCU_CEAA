from django.shortcuts import render
from rest_framework import viewsets
from .models import Task, Student
from .serializers import TaskSerializer, StudentSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
