from django.shortcuts import render

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, PostListSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework.exceptions import PermissionDenied
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action

class PostViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Post.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer
    
    def get_permissions(self):
        if self.action in ["update", "destroy", "partial_update", "create"]:
            return [IsAdminUser()]
        return []
    
    @action(methods=["GET"], detail=True, url_path="like")
    def like_post(self, request, pk=None):
        post = self.get_object()
        post.likes += 1 
        post.save()
        return Response({"detail": "좋아요 됨!", "좋아요개수": post.likes})

    @action(methods=["GET"], detail=False, url_path="top3")
    def top3(self, request):
        top3 = Post.objects.order_by('-likes')[:3]
        serializer = PostSerializer(top3, many=True)
        return Response(serializer.data)

    
    
class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.action in ["update", "destroy", "partial_update"]:
            return [IsOwnerOrReadOnly()]
        return []
    
    def get_object(self):
        obj = super().get_object()
        return obj

class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    # queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post)
        return queryset
    
    
    def create(self, request,post_id=None):
        post = get_object_or_404(Post, id=post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.action in ["list", "create"]:
            return [IsAdminUser()]
        return []
    
    #구현2
    
# class CommentViewSet(viewsets.ModelViewSet):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
    

# class PostCommentViewset(viewsets.ModelViewSet):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
    
#     def list(self,request, post_id=None):
#         post = get_object_or_404(Post, id=post_id)
#         queryset = self.filter_queryset(self.get.queryset().filter(post=post))
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
    
    
#     def create(self, request,post_id=None):
#         post = get_object_or_404(Post, id=post_id)
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(post=post)
#         return Response(serializer.data)