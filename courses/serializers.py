from rest_framework import serializers
from .models import CourseCategory, Course, Module, Lesson, LearningMaterial, Enrollment, LessonProgress


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = '__all__'


class LearningMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningMaterial
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    materials = LearningMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    enrolled_students_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class CourseDetailSerializer(serializers.ModelSerializer):
    category = CourseCategorySerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = '__all__'
