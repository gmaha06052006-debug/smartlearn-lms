from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile
from courses.models import CourseCategory, Course, Module, Lesson, LearningMaterial, Enrollment, LessonProgress
from assignments.models import Assignment, AssignmentSubmission
from quizzes.models import Quiz, Question, QuestionOption, QuizAttempt
from notifications.models import Announcement, Notification
from analytics.models import LearningActivity


class Command(BaseCommand):
    help = 'Seeds complete demonstration data for SmartLearn LMS with top engineering disciplines'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting SmartLearn seed data process...'))

        # =========================================================================
        # 1. User Accounts
        # =========================================================================
        # Admin
        admin_user, created = User.objects.get_or_create(
            username='admin@smartlearn.com',
            defaults={
                'email': 'admin@smartlearn.com',
                'first_name': 'Alex',
                'last_name': 'Morgan',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        admin_user.profile.role = 'admin'
        admin_user.profile.department = 'System Operations & Engineering'
        admin_user.profile.save()

        # Faculty 1: Software & Systems
        faculty_smith, created = User.objects.get_or_create(
            username='dr.smith@smartlearn.com',
            defaults={
                'email': 'dr.smith@smartlearn.com',
                'first_name': 'Alan',
                'last_name': 'Smith',
                'is_staff': False,
            }
        )
        if created:
            faculty_smith.set_password('faculty123')
            faculty_smith.save()
        faculty_smith.profile.role = 'faculty'
        faculty_smith.profile.department = 'Computer Science & Software Engineering'
        faculty_smith.profile.bio = 'Ph.D. in Distributed Systems with 14+ years research in high-throughput database systems and web architecture.'
        faculty_smith.profile.save()

        # Faculty 2: Mechanical & Aerospace
        faculty_elena, created = User.objects.get_or_create(
            username='prof.elena@smartlearn.com',
            defaults={
                'email': 'prof.elena@smartlearn.com',
                'first_name': 'Elena',
                'last_name': 'Rostova',
                'is_staff': False,
            }
        )
        if created:
            faculty_elena.set_password('faculty123')
            faculty_elena.save()
        faculty_elena.profile.role = 'faculty'
        faculty_elena.profile.department = 'Mechanical & Aerospace Engineering'
        faculty_elena.profile.bio = 'Distinguished Chair of Fluid Mechanics and Thermal Systems. Consultant to commercial aviation and aerospace programs.'
        faculty_elena.profile.save()

        # Faculty 3: Electrical & Robotics
        faculty_chen, created = User.objects.get_or_create(
            username='dr.chen@smartlearn.com',
            defaults={
                'email': 'dr.chen@smartlearn.com',
                'first_name': 'Wei',
                'last_name': 'Chen',
                'is_staff': False,
            }
        )
        if created:
            faculty_chen.set_password('faculty123')
            faculty_chen.save()
        faculty_chen.profile.role = 'faculty'
        faculty_chen.profile.department = 'Electrical & Robotics Engineering'
        faculty_chen.profile.bio = 'Leading researcher in embedded digital signal processing, sensor fusion, and autonomous mobile robotics.'
        faculty_chen.profile.save()

        # Student User
        student_user, created = User.objects.get_or_create(
            username='student@smartlearn.com',
            defaults={
                'email': 'student@smartlearn.com',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'is_staff': False,
            }
        )
        if created:
            student_user.set_password('student123')
            student_user.save()
        student_user.profile.role = 'student'
        student_user.profile.department = 'Engineering Science & Technology'
        student_user.profile.student_id = 'SL-2026-8841'
        student_user.profile.save()

        self.stdout.write(self.style.SUCCESS('Validated accounts: admin, faculty (3), student.'))

        # =========================================================================
        # 2. Engineering Categories
        # =========================================================================
        categories_data = [
            ('Software & Cloud Engineering', 'software-cloud-engineering', 'High-availability web applications, distributed backends, and cloud platforms.', 'bi-layers'),
            ('AI & Machine Learning', 'ai-machine-learning', 'Neural networks, transformer architectures, and applied deep learning.', 'bi-cpu'),
            ('Mechanical Engineering', 'mechanical-engineering', 'Thermodynamics, heat transfer, continuum mechanics, and machine design.', 'bi-wrench-adjustable'),
            ('Electrical & Electronics Engineering', 'electrical-engineering', 'Digital signal processing, embedded microcontrollers, and circuit theory.', 'bi-lightning-charge'),
            ('Civil & Structural Engineering', 'civil-engineering', 'Structural dynamics, seismic earthquake design, and continuum infrastructure.', 'bi-building'),
            ('Robotics & Autonomous Systems', 'robotics-engineering', 'Manipulator kinematics, trajectory control, SLAM, and ROS2 autonomous navigation.', 'bi-robot'),
            ('Aerospace Engineering', 'aerospace-engineering', 'Aerodynamics, supersonic flow, and flight vehicle longitudinal dynamics.', 'bi-send'),
            ('Chemical Engineering', 'chemical-engineering', 'Reactor kinetics, catalytic mass transfer, and industrial distillation columns.', 'bi-radioactive'),
            ('Computer Systems Architecture', 'computer-engineering', 'Microarchitecture, pipelining hazards, cache coherence, and GPU acceleration.', 'bi-motherboard'),
            ('Biomedical Engineering', 'biomedical-engineering', 'Biomechanics, bioelectric signal instrumentation, and medical imaging physics.', 'bi-heart-pulse'),
        ]

        category_objs = {}
        for name, slug, desc, icon in categories_data:
            cat, _ = CourseCategory.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'icon': icon}
            )
            # Ensure name and icon are updated if pre-existing
            cat.name = name
            cat.description = desc
            cat.icon = icon
            cat.save()
            category_objs[slug] = cat

        # =========================================================================
        # 3. Helper to build structured courses
        # =========================================================================
        def create_course_with_syllabus(title, slug, category_slug, instructor, difficulty, hours, short_desc, full_desc, modules_data):
            cat = category_objs[category_slug]
            course, _ = Course.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'category': cat,
                    'instructor': instructor,
                    'difficulty': difficulty,
                    'estimated_hours': hours,
                    'is_published': True,
                    'short_description': short_desc,
                    'description': full_desc,
                }
            )
            # Sync metadata
            course.title = title
            course.category = cat
            course.instructor = instructor
            course.difficulty = difficulty
            course.estimated_hours = hours
            course.short_description = short_desc
            course.description = full_desc
            course.is_published = True
            course.save()

            # Ensure all modules & lessons exist
            for mod_idx, (mod_title, mod_desc, lessons_data) in enumerate(modules_data, start=1):
                module, _ = Module.objects.get_or_create(
                    course=course,
                    order=mod_idx,
                    defaults={'title': mod_title, 'description': mod_desc}
                )
                module.title = mod_title
                module.description = mod_desc
                module.save()

                for les_idx, (les_title, duration, content) in enumerate(lessons_data, start=1):
                    lesson, _ = Lesson.objects.get_or_create(
                        module=module,
                        order=les_idx,
                        defaults={
                            'title': les_title,
                            'duration_minutes': duration,
                            'content': content,
                            'video_url': 'https://www.youtube.com/embed/rHux0gMZ3Eg'
                        }
                    )
                    lesson.title = les_title
                    lesson.duration_minutes = duration
                    lesson.content = content
                    lesson.video_url = 'https://www.youtube.com/embed/rHux0gMZ3Eg'
                    lesson.save()

            return course

        # =========================================================================
        # 4. Define Courses with All Required Modules & Lessons
        # =========================================================================

        # -------------------------------------------------------------------------
        # Course 1: Software & Web Architecture
        # -------------------------------------------------------------------------
        c_django = create_course_with_syllabus(
            title='Production Django & Scalable Backend Architecture',
            slug='production-django-rest-api',
            category_slug='software-cloud-engineering',
            instructor=faculty_smith,
            difficulty='intermediate',
            hours=22,
            short_desc='Build resilient, scalable backends using Django 5, DRF, relational MySQL optimization, and enterprise security patterns.',
            full_desc='This master course teaches you how to design, develop, and deploy production-grade Python web backends. You will learn relational database modeling with MySQL, performant RESTful APIs, role-based authorization, cache invalidation strategies, and secure session management.',
            modules_data=[
                (
                    'Module 1: Django Architecture & Clean Relational Modeling',
                    'Fundamental patterns of the Model-View-Template architecture and relational schema modeling.',
                    [
                        ('Django MVT Request Lifecycle & Project Structuring', 25, 'Understanding WSGI/ASGI entrypoints, middleware execution order, model abstraction layers, and modular Django application separation for high-maintainability enterprise repositories.'),
                        ('Relational Schema Design & MySQL 8 Indexes', 30, 'Deep dive into ForeignKeys, OneToOne fields, unique compound constraints, composite B-tree indexes, and zero-downtime migrations in production MySQL environments.'),
                        ('QuerySet Optimization: Avoiding N+1 Queries', 35, 'Comprehensive analysis of select_related (SQL JOINs) versus prefetch_related (batched Python-level joins). Using explain analyze to profile execution plans.'),
                    ]
                ),
                (
                    'Module 2: RESTful API Engineering with Django REST Framework',
                    'Building robust, documented, and authenticated API viewsets and serializers.',
                    [
                        ('ModelSerializers & Custom Field Validations', 35, 'Writing performant DRF serializers, handling complex nested relationships, read-only representations, and field-level validation rules.'),
                        ('ViewSets, Routers, and Content Negotiation', 30, 'Architecting RESTful endpoints with ModelViewSet, custom action decorators, filtering backends, and pagination schemes.'),
                        ('Token & JWT Authentication with RBAC Authorization', 30, 'Securing APIs using stateless JSON Web Tokens (JWT), session cookies with CSRF tokens, and permission classes for student, faculty, and administrator roles.'),
                    ]
                ),
                (
                    'Module 3: Caching, Async Tasks & Reliability',
                    'Speeding up response times with Redis caching and asynchronous job offloading.',
                    [
                        ('Redis Caching & Granular Cache Invalidation', 30, 'Implementing whole-view caching, low-level cache APIs, and cache stampede prevention strategies.'),
                        ('Background Workers with Celery & Message Brokers', 40, 'Decoupling heavy email notifications, report generation, and analytics indexing using Celery workers with Redis or RabbitMQ queues.'),
                        ('Production Readiness: Logging, Health Checks & Gunicorn', 35, 'Configuring structured JSON logging, Sentry error tracking, automated health check probes, and WSGI/Gunicorn concurrency workers.'),
                    ]
                ),
            ]
        )

        # -------------------------------------------------------------------------
        # Course 2: AI & Deep Learning
        # -------------------------------------------------------------------------
        c_ai = create_course_with_syllabus(
            title='Practical Deep Learning & Neural Network Foundations',
            slug='practical-deep-learning',
            category_slug='ai-machine-learning',
            instructor=faculty_smith,
            difficulty='advanced',
            hours=26,
            short_desc='Master transformer architectures, backpropagation mathematics, loss landscape optimization, and PyTorch model fine-tuning.',
            full_desc='A comprehensive dive into modern artificial intelligence. Covers linear algebra intuition, backpropagation, attention mechanisms, convolution backbones, and practical PyTorch workflows on modern GPU accelerators.',
            modules_data=[
                (
                    'Module 1: Mathematical Foundations & Gradient Descent',
                    'Calculus, linear algebra, computational graphs, and loss surfaces.',
                    [
                        ('Tensors, Matrix Factorizations & Computational Graphs', 35, 'Vectors, matrices, higher-order tensors, and automatic reverse-mode differentiation algorithms in computational graphs.'),
                        ('Stochastic Gradient Descent, Momentum, and AdamW', 40, 'Analyzing optimization landscapes, saddle points, adaptive learning rate schedules, weight decay regularization, and convergence rates.'),
                        ('Backpropagation Derivation from First Principles', 40, 'Step-by-step mathematical derivation of chain rule gradients across dense multi-layer perceptrons (MLP).'),
                    ]
                ),
                (
                    'Module 2: Convolutional & Sequential Architectures',
                    'Computer vision backbones and sequence models.',
                    [
                        ('2D Convolutions, Pooling & Residual Connections (ResNet)', 45, 'Kernel filtering, receptive fields, batch normalization mechanics, and how residual skip connections prevent vanishing gradients.'),
                        ('Recurrent Networks & Long Short-Term Memory (LSTM)', 35, 'Cell state highways, input/forget/output gating mechanisms, and overcoming gradient degradation in sequential modeling.'),
                        ('Sequence-to-Sequence Modeling & Attention Mechanism', 40, 'Bahdanau and Luong attention mechanics, alignment vectors, and the intuition bridging RNNs to pure attention networks.'),
                    ]
                ),
                (
                    'Module 3: Transformer Architectures & LLM Fine-Tuning',
                    'Modern generative artificial intelligence and attention mechanism.',
                    [
                        ('Self-Attention & Scaled Dot-Product Mechanics', 45, 'Query, Key, and Value projections, multi-head attention parallelism, positional encodings, and causal decoding masks.'),
                        ('The Transformer Architecture: Encoder & Decoder Stacks', 50, 'Layer normalization (Post-LN vs Pre-LN), feed-forward dimension expansion, and tokenization algorithms (BPE, WordPiece).'),
                        ('Parameter-Efficient Fine-Tuning (PEFT & LoRA)', 45, 'Low-Rank Adaptation (LoRA) mathematics, quantization techniques (QLoRA), and fine-tuning open-source LLMs on specialized domains.'),
                    ]
                ),
            ]
        )

        # -------------------------------------------------------------------------
        # Course 3: Mechanical Engineering: Advanced Thermodynamics & Heat Transfer
        # -------------------------------------------------------------------------
        c_thermo = create_course_with_syllabus(
            title='Applied Thermodynamics & Heat Transfer Engineering',
            slug='applied-thermodynamics-heat-transfer',
            category_slug='mechanical-engineering',
            instructor=faculty_elena,
            difficulty='intermediate',
            hours=28,
            short_desc='Analyze thermodynamic energy cycles, conduction networks, convective boundary layers, and industrial heat exchangers.',
            full_desc='Designed to ABET engineering accreditation benchmarks. This curriculum provides comprehensive mastery of thermodynamic law applications, steady and transient conduction, laminar/turbulent forced convection, thermal radiation view factors, and industrial shell-and-tube heat exchanger sizing.',
            modules_data=[
                (
                    'Module 1: Fundamental Laws of Thermodynamics & Energy Balances',
                    'Mastering energy, entropy, exergy, and thermodynamic power generation cycles.',
                    [
                        ('First Law Energy Balances for Open and Closed Control Volumes', 35, 'Derivation of the first law for control volumes: mass conservation, enthalpy flow, shaft work, and energy conservation across turbines, compressors, and nozzles.'),
                        ('Second Law, Entropy Generation & Irreversibility Analysis', 40, 'Clausius inequality, entropy generation in irreversible processes, isentropic efficiencies, and maximum theoretical work output.'),
                        ('Vapor Power & Gas Turbine Cycles (Rankine & Brayton Cycles)', 45, 'Superheating, reheat and regenerative feed-water heaters in Rankine steam plants. Intercooling and regeneration in Brayton gas turbine cycles.'),
                    ]
                ),
                (
                    'Module 2: Conduction & Thermal Resistance Networks',
                    'Differential heat conduction equations, finned extended surfaces, and transient cooling.',
                    [
                        ('Differential Equations of Heat Conduction & Boundary Conditions', 35, 'Fourier’s law, Laplacian thermal diffusion equations in Cartesian, cylindrical, and spherical coordinate systems, with Dirichlet and Neumann boundary conditions.'),
                        ('Extended Surfaces: Fin Efficiency & Fin Effectiveness', 35, 'Mathematical solutions for straight and annular fins. Calculating convective heat dissipation enhancements and optimal spacing in heat sinks.'),
                        ('Transient Conduction: Lumped Capacitance & Spatial Variation', 40, 'Biot number criteria (Bi < 0.1), characteristic time constants, Fourier numbers, and 1D transient analytical Heisler/Grober solutions.'),
                    ]
                ),
                (
                    'Module 3: Forced & Natural Convection Heat Transfer',
                    'Boundary layer fluid mechanics, empirical correlations, and buoyancy-driven flow.',
                    [
                        ('Hydrodynamic & Thermal Boundary Layer Physics', 40, 'Prandtl number significance, velocity boundary layer thickness, thermal boundary layer growth, and Reynolds analogy for friction and heat transfer.'),
                        ('Forced Convection Correlations for Pipes, Ducts & Tube Bundles', 45, 'Dittus-Boelter, Gnielinski, and Churchill-Bernstein empirical correlations for turbulent internal flows and external cross-flow past staggered tube banks.'),
                        ('Natural Convection & Buoyancy: Grashof and Rayleigh Numbers', 35, 'Boussinesq approximation, vertical plate buoyancy flow, Rayleigh number transition to turbulence, and enclosure convection modeling.'),
                    ]
                ),
                (
                    'Module 4: Radiative Heat Transfer & Industrial Heat Exchangers',
                    'Blackbody radiation, view factors, LMTD, and NTU industrial sizing.',
                    [
                        ('Thermal Radiation: Planck, Wien & Stefan-Boltzmann Laws', 35, 'Blackbody spectral distribution, surface emissivity, absorptivity, gray surface approximations, and Kirchhoff’s law of thermal radiation.'),
                        ('Radiation View Factors & Radiation Shields', 40, 'Geometric view factor reciprocity and summation rules. Hottel’s crossed-strings method, and heat transfer reduction through multi-layer radiation shields.'),
                        ('Heat Exchanger Design: LMTD & Effectiveness-NTU Method', 50, 'Shell-and-tube and plate heat exchangers. Overall heat transfer coefficient U, fouling factors, Log Mean Temperature Difference (LMTD) corrections, and NTU sizing curves.'),
                    ]
                ),
            ]
        )

        # -------------------------------------------------------------------------
        # Course 4: Electrical & Electronics Engineering: DSP & Embedded Systems
        # -------------------------------------------------------------------------
        c_dsp = create_course_with_syllabus(
            title='Digital Signal Processing & Embedded ARM Microcontrollers',
            slug='digital-signal-processing-embedded-arm',
            category_slug='electrical-engineering',
            instructor=faculty_chen,
            difficulty='intermediate',
            hours=24,
            short_desc='Design FIR/IIR filters, compute real-time FFTs, and implement signal processing pipelines on ARM Cortex-M microcontrollers.',
            full_desc='Bridge rigorous signal processing theory with practical embedded engineering. You will implement discrete Fourier transforms, Parks-McClellan FIR filters, and bilinear IIR filters, then execute them in real time on 32-bit ARM Cortex-M hardware utilizing CMSIS-DSP, DMA, and ADC peripherals.',
            modules_data=[
                (
                    'Module 1: Discrete-Time Signals & LTI Systems',
                    'Sampling theorem, linear time-invariant convolution, and stability analysis.',
                    [
                        ('Nyquist-Shannon Sampling Theorem & Anti-Aliasing Filters', 35, 'Bandwidth limits, aliasing distortions in the frequency domain, reconstruction sinc filters, and analog front-end anti-aliasing design.'),
                        ('Discrete Convolution & LTI System Impulse Responses', 35, 'Linearity, time-invariance, causality, stability criteria, and step-by-step graphical and matrix computation of discrete-time convolution.'),
                        ('The Z-Transform, Region of Convergence (ROC) & Stability', 40, 'Bilateral Z-transform, pole-zero plots in the complex z-plane, and mapping bounded-input bounded-output (BIBO) stability relative to the unit circle.'),
                    ]
                ),
                (
                    'Module 2: Frequency Domain Analysis & Fast Fourier Transform (FFT)',
                    'Bridging continuous spectra to computational radix algorithms.',
                    [
                        ('Discrete-Time Fourier Transform (DTFT) & Spectral Properties', 35, 'Continuous frequency representations of discrete signals, periodic spectra, symmetry properties, and frequency shift theorems.'),
                        ('Discrete Fourier Transform (DFT) & Spectral Leakage', 35, 'Sampling the DTFT, circular convolution, frequency bin resolution, and applying Hann, Hamming, and Blackman windowing functions to eliminate spectral leakage.'),
                        ('Radix-2 Decimation-in-Time Cooley-Tukey FFT Algorithm', 45, 'Butterfly operations, bit-reversal permutation, twiddle factor symmetries, and reducing computational complexity from O(N^2) to O(N log N).'),
                    ]
                ),
                (
                    'Module 3: Digital Filter Design: FIR & IIR',
                    'Synthesis of finite and infinite impulse response digital filters.',
                    [
                        ('Linear-Phase FIR Filter Design using Windowing Methods', 40, 'Four types of linear-phase FIR filters, constant phase delay, group delay, and passband ripple vs stopband attenuation tradeoffs.'),
                        ('IIR Filter Design via Bilinear Transformation', 40, 'Analog prototypes (Butterworth, Chebyshev), continuous-to-discrete s-plane to z-plane mapping, frequency warping, and pre-warping formulas.'),
                        ('Filter Realizations & Finite Word-Length Quantization Effects', 35, 'Direct Form I, Direct Form II Transposed, and Cascade/Parallel biquad structures. Limit cycle oscillations, coefficient quantization, and overflow mitigation.'),
                    ]
                ),
                (
                    'Module 4: Real-Time Execution on ARM Cortex-M Microcontrollers',
                    'Low-latency audio and sensor processing on embedded silicon.',
                    [
                        ('ARM Cortex-M Architecture & CMSIS-DSP SIMD Intrinsics', 40, 'Thumb-2 instruction set, FPU hardware acceleration, SIMD instructions, and leveraging optimized CMSIS-DSP assembly routines for vector dot products.'),
                        ('DMA Double-Buffering & ADC/DAC Interrupt Pipelines', 45, 'Configuring ping-pong circular DMA buffers to eliminate CPU polling latency during continuous ADC analog audio streaming.'),
                        ('Real-Time Digital Audio Equalizer Project Implementation', 50, 'Building a 3-band parametric equalizer firmware running at 48 kHz sampling rate with real-time biquad filtering and negligible latency.'),
                    ]
                ),
            ]
        )

        # -------------------------------------------------------------------------
        # Course 5: Civil & Structural Engineering: Structural Dynamics & Seismic Design
        # -------------------------------------------------------------------------
        c_civil = create_course_with_syllabus(
            title='Structural Dynamics & Seismic Earthquake Engineering',
            slug='structural-dynamics-seismic-engineering',
            category_slug='civil-engineering',
            instructor=faculty_elena,
            difficulty='advanced',
            hours=26,
            short_desc='Analyze vibration dynamics of structures, response spectra, ductile concrete detailing, and seismic base isolation.',
            full_desc='Comprehensive structural engineering curriculum focusing on single- and multi-degree-of-freedom dynamic systems, response spectrum analysis of earthquake ground motions, plastic hinges, and ductile seismic detailing per modern international building codes.',
            modules_data=[
                (
                    'Module 1: Indeterminate Structural Analysis & Stiffness Formulations',
                    'Energy principles, virtual displacements, and matrix stiffness formulation.',
                    [
                        ('Virtual Work Principles & Castigliano’s Deflection Theorems', 35, 'Complementary energy, strain energy stored in flexure and shear, and calculating deflections in statically indeterminate truss and beam structures.'),
                        ('Slope-Deflection Method & Moment Distribution for Rigid Frames', 45, 'Rotational stiffness, carry-over factors, fixed-end moments, and solving multi-bay multi-story unbraced sway frames.'),
                        ('Direct Stiffness Matrix Method for 2D/3D Frame Structures', 45, 'Local vs global coordinate transformations, elemental stiffness matrices, global assembly, and enforcing displacement boundary conditions.'),
                    ]
                ),
                (
                    'Module 2: Structural Dynamics of SDOF & MDOF Systems',
                    'Equations of dynamic motion, natural frequencies, and mode shapes.',
                    [
                        ('Single Degree of Freedom (SDOF) Undamped & Damped Free Vibration', 35, 'Mass-spring-damper idealizations, natural circular frequency, critical damping ratio, and logarithmic decrement measurement.'),
                        ('Dynamic Response to Harmonic, Periodic & Blast Excitations', 40, 'Dynamic magnification factor (DMF), resonance phenomena, phase lag, and Duhamel integral convolution for arbitrary transient loading.'),
                        ('Multi-Degree of Freedom (MDOF) Systems: Eigenvalues & Mode Shapes', 50, 'Coupled equations of motion, mass and stiffness matrix formulations, characteristic eigenvalue equations, modal orthogonality, and modal expansion.'),
                    ]
                ),
                (
                    'Module 3: Earthquake Ground Motion & Response Spectra',
                    'Seismic hazard analysis, peak acceleration, and elastic/inelastic response spectra.',
                    [
                        ('Seismic Fault Ruptures & Ground Motion Wave Propagation', 35, 'P-waves, S-waves, Rayleigh and Love surface waves, attenuation relationships, and analyzing historic earthquake accelerograms.'),
                        ('Elastic Response Spectra & Peak Ground Acceleration (PGA)', 40, 'Construction of tripartite response spectra (displacement, velocity, pseudo-acceleration) and site soil amplification factors.'),
                        ('Inelastic Response, Ductility Capacity & Overstrength Factors', 45, 'Ductility reduction factor (R), plastic hinge dissipation, Newmark-Hall inelastic spectra, and energy balance criteria during strong seismic shaking.'),
                    ]
                ),
                (
                    'Module 4: Seismic Resistant Design & Base Isolation Systems',
                    'Code-based lateral force procedures and modern structural damping.',
                    [
                        ('Equivalent Lateral Force (ELF) Procedure & Base Shear Distribution', 40, 'Fundamental period estimation, seismic importance factors, vertical distribution of lateral forces, and torsional eccentricity calculations.'),
                        ('Ductile Detailing of Reinforced Concrete Beams, Columns & Shear Walls', 45, 'Confining hoop reinforcement, strong-column weak-beam hierarchy, shear reinforcement capacity against brittle diagonal tension, and plastic hinge development.'),
                        ('Seismic Base Isolation, Elastomeric Bearings & Tuned Mass Dampers', 40, 'Period elongation through elastomeric and lead-rubber bearings, damping dissipation mechanics, and installing tuned mass dampers in high-rise skyscrapers.'),
                    ]
                ),
            ]
        )

        # -------------------------------------------------------------------------
        # Course 6: Robotics & Mechatronics: Autonomous Navigation & Kinematics
        # -------------------------------------------------------------------------
        c_robotics = create_course_with_syllabus(
            title='Autonomous Mobile Robotics: Kinematics, SLAM & ROS2',
            slug='autonomous-robotics-kinematics-slam-ros2',
            category_slug='robotics-engineering',
            instructor=faculty_chen,
            difficulty='advanced',
            hours=30,
            short_desc='Master forward/inverse kinematics, extended Kalman filtering, LiDAR SLAM, and ROS2 autonomous navigation stacks.',
            full_desc='Engineered for robotics engineers and autonomy researchers. Master homogeneous spatial transformations, Denavit-Hartenberg manipulator kinematics, mobile robot differential drive odometry, sensor fusion with EKF, 2D/3D SLAM mapping, and ROS2 Nav2 motion planning algorithms.',
            modules_data=[
                (
                    'Module 1: Spatial Descriptions & Manipulator Kinematics',
                    'Coordinate frames, rotation matrices, and analytical robot kinematics.',
                    [
                        ('Rotations, Homogeneous Coordinates & SE(3) Transformations', 35, 'Euler angles, roll-pitch-yaw, unit quaternions, and 4x4 homogeneous transformation matrices for rigid body coordinate frames in 3D space.'),
                        ('Denavit-Hartenberg (DH) Forward Kinematic Modeling', 40, 'Standard and modified DH parameter conventions: link length, twist, offset, and joint angle. Assigning reference frames to industrial serial arms.'),
                        ('Inverse Kinematics: Algebraic, Geometric & Numerical Solvers', 45, 'Pieper’s condition for 6-DOF arms with spherical wrists, closed-form geometric solutions, and iterative Newton-Raphson/Damped Least Squares solvers.'),
                    ]
                ),
                (
                    'Module 2: Differential Drive Kinematics & Manipulator Jacobians',
                    'Velocities, singularities, and mobile platform odometry.',
                    [
                        ('Differential Drive & Omnidirectional Mobile Robot Kinematics', 35, 'Instantaneous center of curvature (ICC), forward/inverse velocity models for two-wheel differential drive and four-wheel mecanum robots.'),
                        ('Geometric and Analytical Jacobians of Robot Manipulators', 40, 'Mapping joint velocities to end-effector linear and angular velocities. Propagating twist vectors across sequential kinematic links.'),
                        ('Kinematic Singularities & Manipulability Ellipsoids', 35, 'Decoupling arm and wrist singularities, determinant criteria, condition numbers, and Yoshikawa’s manipulability measure.'),
                    ]
                ),
                (
                    'Module 3: Sensor Fusion & SLAM (Simultaneous Localization and Mapping)',
                    'LiDAR perception, Kalman state estimation, and occupancy grid maps.',
                    [
                        ('Sensor Fusion with Extended Kalman Filters (EKF)', 45, 'Linearizing nonlinear kinematics and observation models with Jacobians. Fusing IMU gyroscopes, wheel encoders, and GPS positioning in real time.'),
                        ('LiDAR Point Cloud Processing & Iterative Closest Point (ICP)', 40, 'Point cloud filtering (voxel grid downsampling, outlier removal), surface normal computation, and point-to-plane ICP scan matching algorithms.'),
                        ('Graph-Based SLAM & Pose Graph Optimization', 45, 'Front-end scan matching, back-end nonlinear least-squares pose graph optimization (g2o, GTSAM), and loop closure detection using bag-of-words.'),
                    ]
                ),
                (
                    'Module 4: Autonomous Motion Planning & ROS2 Nav2 Implementation',
                    'Path searching, trajectory optimization, and deployment on ROS2 Humble.',
                    [
                        ('Global Path Planning Algorithms: A*, Dijkstra & RRT*', 40, 'Configuration space obstacles (C-space inflation), heuristic path searching on costmaps, and asymptotically optimal Rapidly-exploring Random Trees (RRT*).'),
                        ('Local Trajectory Generation & Model Predictive Control (MPC)', 40, 'Dynamic Window Approach (DWA), Timed-Elastic-Band (TEB) planners, and real-time receding horizon Model Predictive Control for obstacle avoidance.'),
                        ('End-to-End Autonomous Navigation Pipeline in ROS2 Humble', 50, 'Configuring Nav2 costmaps, BT (Behavior Tree) navigators, lifecycle nodes, AMCL probabilistic localization, and testing in Gazebo physics simulations.'),
                    ]
                ),
            ]
        )

        # -------------------------------------------------------------------------
        # Course 7: Aerospace Engineering: Aerodynamics & Flight Mechanics
        # -------------------------------------------------------------------------
        c_aero = create_course_with_syllabus(
            title='Aerodynamics & Flight Vehicle Dynamics',
            slug='aerodynamics-flight-vehicle-dynamics',
            category_slug='aerospace-engineering',
            instructor=faculty_elena,
            difficulty='advanced',
            hours=25,
            short_desc='Master incompressible potential flow, supersonic shock wave physics, finite wing lift distribution, and aircraft trim stability.',
            full_desc='Comprehensive aerospace curriculum covering potential flow theory, circulation lift, Prandtl’s lifting-line finite wing induced drag, supersonic normal/oblique shock waves, aircraft drag polars, and longitudinal dynamic stability modes (phugoid and short-period).',
            modules_data=[
                (
                    'Module 1: Fluid Dynamics & Incompressible Potential Aerodynamics',
                    'Fundamental continuum mechanics and potential flow elementary solutions.',
                    [
                        ('Continuity, Momentum & Navier-Stokes Equations for Aerodynamics', 35, 'Substantial derivatives, stress tensor formulations, Reynolds-averaged Navier-Stokes equations, and boundary layer assumptions.'),
                        ('Elementary Potential Flows & Kutta-Joukowski Lift Theorem', 40, 'Superposition of uniform flow, source/sink pairs, doublets, and point vortices. Magnus effect and deriving the Kutta-Joukowski theorem: L = rho * V * Gamma.'),
                        ('Classical Thin Airfoil Theory & Camber Line Geometry', 40, 'Vortex sheet distribution on the mean camber line, Fourier series expansion of circulation, and calculating zero-lift angle of attack and pitching moment.'),
                    ]
                ),
                (
                    'Module 2: Finite Wing Theory & Induced Drag Optimization',
                    '3D wing aerodynamics, downwash, and tip vortex dynamics.',
                    [
                        ('Prandtl’s Lifting-Line Theory for Finite Wings', 40, 'Trailing vortex filaments, downwash velocity, effective angle of attack, and solving the fundamental lifting-line integro-differential equation.'),
                        ('Elliptic Lift Distribution & Minimum Induced Drag', 35, 'Mathematical proof of elliptic wing planform optimality, span efficiency factor e, and wing aspect ratio aerodynamic tradeoffs.'),
                        ('Wing Swept Planforms, Delta Wings & Transonic Buffeting', 35, 'Critical Mach number, swept-back wing isobar obliquity, leading-edge vortex lift on delta wings, and supercritical airfoil shock attenuation.'),
                    ]
                ),
                (
                    'Module 3: Compressible Gas Dynamics & Supersonic Shock Waves',
                    'Thermodynamics of high-speed gas flows and shock mechanics.',
                    [
                        ('Isentropic Stagnation Relations & Speed of Sound', 35, 'Compressibility criteria, total vs static temperature and pressure, acoustic wave speed derivation, and converging-diverging de Laval nozzles.'),
                        ('Normal & Oblique Shock Waves across Supersonic Wedges', 45, 'Rankine-Hugoniot jump relations, shock polar diagrams, detachment angles, pressure ratio across oblique shocks, and wave drag generation.'),
                        ('Prandtl-Meyer Expansion Fans & Supersonic Aerofoils', 40, 'Prandtl-Meyer expansion function, centered wave physics, supersonic flat-plate and diamond-wedge airfoil pressure integrations.'),
                    ]
                ),
                (
                    'Module 4: Flight Vehicle Performance & Longitudinal Stability',
                    'Aircraft power required, static trim, and dynamic flight modes.',
                    [
                        ('Aircraft Drag Polar, Maximum Range & Endurance Velocities', 35, 'Parasite and induced drag parabolic polar, minimum drag velocity, thrust required for level unaccelerated flight, and climb ceilings.'),
                        ('Static Longitudinal Stability, Neutral Point & Static Margin', 40, 'Pitching moment derivative Cm_alpha, horizontal tail aerodynamic center, downwash gradient, stick-fixed neutral point, and static margin criteria.'),
                        ('Dynamic Longitudinal Stability: Phugoid & Short-Period Modes', 45, 'Small-perturbation equations of motion, linearized stability derivatives, characteristic quartics, short-period pitch oscillations, and phugoid energy exchanges.'),
                    ]
                ),
            ]
        )

        # -------------------------------------------------------------------------
        # Course 8: Chemical Engineering: Chemical Reaction Kinetics & Separation
        # -------------------------------------------------------------------------
        c_chem = create_course_with_syllabus(
            title='Chemical Reaction Kinetics & Industrial Separation Processes',
            slug='chemical-reaction-kinetics-separation',
            category_slug='chemical-engineering',
            instructor=faculty_smith,
            difficulty='intermediate',
            hours=24,
            short_desc='Design ideal CSTR/PFR reactors, analyze heterogeneous catalysis, and size multi-stage fractional distillation columns.',
            full_desc='Rigorous chemical engineering curriculum covering mole balances on ideal batch, CSTR, and plug-flow reactors, non-isothermal energy balances, Langmuir-Hinshelwood heterogeneous catalysis, Thiele modulus diffusion, and multi-stage distillation column hydraulics.',
            modules_data=[
                (
                    'Module 1: Mole Balances & Ideal Chemical Reactor Sizing',
                    'Fundamental reactor design equations for homogeneous liquid and gas reactions.',
                    [
                        ('General Mole Balance & Reactor Design Equations (Batch, CSTR, PFR)', 35, 'Deriving governing design equations from first principles for batch, continuous stirred-tank (CSTR), and plug-flow reactors (PFR).'),
                        ('Reaction Kinetics, Rate Laws & Stoichiometric Tables', 35, 'Power law rate equations, elementary vs non-elementary reactions, temperature dependence via Arrhenius equation, and phase expansion factors.'),
                        ('Sizing Single and Multi-Reactor Networks in Series and Parallel', 40, 'Levenspiel graphical plots, comparison of CSTR and PFR volumes for various reaction orders, recycle reactors, and optimal network design.'),
                    ]
                ),
                (
                    'Module 2: Non-Isothermal Reactor Design & Thermal Runaway',
                    'Coupling energy balances with reaction rates for safe exothermic operations.',
                    [
                        ('Steady-State Energy Balances for Continuous Flow Reactors', 35, 'Enthalpy of reaction, heat of generation vs heat of removal curves, adiabatic operation, and calculating conversion-temperature profiles.'),
                        ('Multiple Steady States & Reactor Thermal Ignition', 40, 'Van Heerden heat generation curves, operating point stability criteria, hysteresis during thermal transitions, and ignition/extinction phenomena.'),
                        ('Thermal Runaway Hazards & Emergency Pressure Relief Sizing', 40, 'Kinetics of auto-accelerating reactions, runaway runaway induction times, cooling jacket failure analysis, and DIERS relief valve sizing.'),
                    ]
                ),
                (
                    'Module 3: Heterogeneous Catalysis & Transport Phenomena',
                    'Surface reactions, external mass transfer, and internal pore diffusion.',
                    [
                        ('Heterogeneous Catalytic Mechanisms (Langmuir-Hinshelwood)', 35, 'Physical adsorption vs chemisorption, Langmuir isotherms, rate-limiting surface reaction steps, and dual-site catalytic kinetics.'),
                        ('External Mass Transfer Resistance across Catalytic Pellets', 35, 'Boundary layer mass transfer coefficients, Sherwood and Schmidt dimensionless numbers, and Mears criterion for external diffusion limitations.'),
                        ('Internal Pore Diffusion & Thiele Modulus Effectiveness Factor', 45, 'Knudsen and molecular diffusion in porous media, second-order differential diffusion-reaction equations, Thiele modulus, and internal effectiveness factors.'),
                    ]
                ),
                (
                    'Module 4: Separation Operations: Multi-Stage Distillation Columns',
                    'Thermodynamics of vapor-liquid equilibria and column design hydraulics.',
                    [
                        ('Vapor-Liquid Equilibrium (VLE) & Non-Ideal Activity Coefficients', 35, 'Raoult’s Law, relative volatility, bubble and dew point algorithms, and Wilson / NRTL non-ideal thermodynamic activity coefficient models.'),
                        ('McCabe-Thiele Method for Binary Fractional Distillation', 45, 'Operating lines (rectifying and stripping sections), feed thermal condition q-line, minimum reflux ratio, and stepping off theoretical equilibrium stages.'),
                        ('Packed and Tray Column Hydraulics, Flooding & Mass Transfer Units', 40, 'Sieve, valve, and bubble cap tray efficiencies. Packed column flooding correlations, pressure drops, Height of an Equivalent Theoretical Plate (HETP), and transfer units.'),
                    ]
                ),
            ]
        )

        # -------------------------------------------------------------------------
        # Course 9: Computer Systems Architecture: Pipelining & High Performance
        # -------------------------------------------------------------------------
        c_arch = create_course_with_syllabus(
            title='Advanced Computer Architecture & Scalable Parallel Systems',
            slug='advanced-computer-architecture-parallel',
            category_slug='computer-engineering',
            instructor=faculty_smith,
            difficulty='advanced',
            hours=24,
            short_desc='Analyze out-of-order superscalar execution, branch predictors, MESI cache coherence, and GPU compute architectures.',
            full_desc='Comprehensive hardware architecture curriculum covering modern RISC-V and ARM64 instruction set principles, dynamic branch prediction, Tomasulo’s out-of-order execution, multi-level cache hierarchies, directory-based cache coherence, and GPU streaming multiprocessor pipelines.',
            modules_data=[
                (
                    'Module 1: Instruction Set Architectures & Dynamic Pipelining',
                    'Instruction set principles, 5-stage hazard mitigation, and speculative execution.',
                    [
                        ('RISC-V vs ARM64 ISA Principles & Addressing Modes', 35, 'Load-store architecture philosophies, instruction encoding formats, fixed-width vs variable-width tradeoffs, and ABI calling conventions.'),
                        ('Pipeline Hazards: Structural, Data Forwarding & Control Resolution', 40, 'Data dependencies, RAW/WAR/WAW hazards, register forwarding networks, pipeline interlocks, and branch delay slots.'),
                        ('Dynamic Branch Prediction: 2-Bit Saturating Counters to TAGE', 45, 'Branch target buffers (BTB), local/global history registers, tournament predictors, and the state-of-the-art TAGE predictor architecture.'),
                    ]
                ),
                (
                    'Module 2: Superscalar Execution & Out-of-Order Processing',
                    'Instruction level parallelism (ILP) and speculative scheduling.',
                    [
                        ('Tomasulo’s Algorithm & Register Renaming', 45, 'Eliminating false anti- and output-dependencies, reservation stations, common data bus (CDB) broadcasting, and hardware tag tracking.'),
                        ('Reorder Buffers (ROB) & Precise Exception Handling', 40, 'Speculative register writes, in-order retirement mechanisms, handling branch mispredictions, and architectural state recovery.'),
                        ('Memory Disambiguation & Store-to-Load Forwarding', 35, 'Load-store queues (LSQ), speculative load execution past unresolved store addresses, and dynamic memory aliasing detection.'),
                    ]
                ),
                (
                    'Module 3: Memory Hierarchies & Cache Coherence Protocols',
                    'SRAM cache organization, miss classification, and multiprocessor coherence.',
                    [
                        ('Multi-Level Cache Design: Associativity, Replacement & MSHRs', 35, 'Direct-mapped vs N-way set associative caches, LRU and Pseudo-LRU policies, write-through vs write-back, and non-blocking caches with MSHRs.'),
                        ('Snooping-Based MESI & MOESI Cache Coherence Protocols', 45, 'Shared bus broadcast protocols, Modified-Exclusive-Shared-Invalid state machine transitions, invalidation traffic, and false sharing mitigation.'),
                        ('Directory-Based Cache Coherence for Scalable NUMA Systems', 40, 'Point-to-point network messages, distributed directory bitmasks, home node transaction serialization, and scalable multicore interconnects.'),
                    ]
                ),
                (
                    'Module 4: SIMD, GPU Architecture & Heterogeneous Acceleration',
                    'Vector pipelines, warp scheduling, and high-bandwidth accelerators.',
                    [
                        ('Vector Architecture Principles: AVX-512 & ARM SVE', 35, 'Vector length agnostic (VLA) programming, predication masks, strided gather/scatter memory operations, and loop vectorization compiler optimizations.'),
                        ('GPU Microarchitecture: Streaming Multiprocessors & Warps', 45, 'SIMT (Single Instruction Multiple Threads) execution model, warp divergence branch handling, shared memory banks, and latency hiding via massive multithreading.'),
                        ('Heterogeneous Interconnects & High-Bandwidth Memory (HBM3)', 40, 'Unified virtual memory (UVM), cache-coherent CPU-GPU interconnects (CXL, NVLink), and 3D-stacked High-Bandwidth Memory (HBM3) throughput characteristics.'),
                    ]
                ),
            ]
        )

        # -------------------------------------------------------------------------
        # Course 10: Biomedical Engineering: Biomechanics & Instrumentation
        # -------------------------------------------------------------------------
        c_bme = create_course_with_syllabus(
            title='Biomechanical Systems & Biomedical Instrumentation',
            slug='biomechanical-systems-biomedical-instrumentation',
            category_slug='biomedical-engineering',
            instructor=faculty_elena,
            difficulty='intermediate',
            hours=22,
            short_desc='Analyze human musculoskeletal biomechanics, bioelectric instrumentation (ECG/EMG), and medical imaging physics.',
            full_desc='Interdisciplinary engineering curriculum covering continuum viscoelastic tissue mechanics, joint force analysis, biopotential electrodes, low-noise instrumentation amplifiers for ECG and EMG signals, and the physical principles of Computed Tomography (CT) and Magnetic Resonance Imaging (MRI).',
            modules_data=[
                (
                    'Module 1: Continuum Biomechanics & Musculoskeletal Dynamics',
                    'Viscoelastic modeling of biological tissues and joint kinematics.',
                    [
                        ('Viscoelasticity of Soft Biological Tissues (Maxwell & Kelvin-Voigt)', 35, 'Creep, stress relaxation, hysteresis, and mechanical characterization of ligaments, tendons, and vascular walls using linear viscoelastic models.'),
                        ('Bone Mechanics, Wolff’s Law & Stress Shielding in Implants', 35, 'Cortical vs trabecular bone anisotropy, fatigue micro-fractures, adaptive bone remodeling (Wolff’s law), and modulus mismatch in titanium hip prostheses.'),
                        ('Inverse Dynamics of Gait & Human Joint Reaction Forces', 40, 'Ground reaction force plate measurement, 3D motion capture marker kinematics, and recursive Newton-Euler joint moment calculations at the knee and hip.'),
                    ]
                ),
                (
                    'Module 2: Bioelectric Signals & Diagnostic Sensor Design',
                    'Electrophysiology, electrode electrochemistry, and low-noise frontend amplifiers.',
                    [
                        ('Cellular Electrophysiology: Nernst & Goldman-Hodgkin-Katz Equations', 35, 'Ionic equilibrium potentials (Na+, K+, Cl-), voltage-gated ion channels, action potential propagation down myelinated axon fibers.'),
                        ('Biopotential Electrodes & Half-Cell Potential Chemistry', 35, 'Silver/Silver-Chloride (Ag/AgCl) electrode interface, electrode-skin impedance matching, motion artifact minimization, and polarizable vs non-polarizable interfaces.'),
                        ('Precision Instrumentation Amplifiers & ECG Circuit Design', 45, 'Three-op-amp instrumentation topologies, common-mode rejection ratio (CMRR > 100 dB), driven-right-leg (DRL) circuitry, and active notch filtering for 50/60 Hz powerline hum.'),
                    ]
                ),
                (
                    'Module 3: Medical Imaging Principles (CT, MRI & Ultrasound)',
                    'Diagnostic imaging physics and tomographic reconstruction algorithms.',
                    [
                        ('X-Ray Attenuation & Radon Transform CT Image Reconstruction', 40, 'Beer-Lambert attenuation, bremsstrahlung and characteristic radiation, Radon transform projections, and Filtered Backprojection (FBP) reconstruction.'),
                        ('Magnetic Resonance Imaging (MRI): Nuclear Spins & RF Excitation', 45, 'Larmor frequency, hydrogen proton magnetization vectors, 90-degree RF pulses, T1 longitudinal and T2 transverse relaxation times, and gradient spatial encoding.'),
                        ('Diagnostic Ultrasound: Acoustic Impedance & Doppler Velocimetry', 35, 'Piezoelectric ceramic transducers, acoustic impedance reflection coefficients, A-mode, B-mode imaging, and pulsed-wave Doppler blood flow velocimetry.'),
                    ]
                ),
                (
                    'Module 4: Neural Engineering, Bionics & Rehabilitation Tech',
                    'Neural stimulation, prosthetics, and regulatory standards.',
                    [
                        ('Myoelectric Pattern Recognition for Bionic Upper-Limb Prostheses', 40, 'Surface EMG feature extraction (mean absolute value, zero crossings, wave-form length), linear discriminant analysis classifiers, and proportional motor control.'),
                        ('Neural Interfaces: Cochlear Implants & Deep Brain Stimulation', 40, 'Biphasic charge-balanced stimulation pulses to prevent tissue electrolysis, multi-channel cochlear tonotopic mapping, and subthalamic nucleus neurostimulation.'),
                        ('Medical Device Safety Standards (IEC 60601-1 & ISO 13485)', 35, 'Patient leakage currents, electrical isolation barriers, risk management per ISO 14971, and FDA 510(k) premarket notification pathways.'),
                    ]
                ),
            ]
        )

        self.stdout.write(self.style.SUCCESS('Successfully verified all 10 core engineering courses, modules, and lessons.'))

        # =========================================================================
        # 5. Course Progress Setup (Exact, Mathematically Correct Progress)
        # =========================================================================
        self.stdout.write(self.style.NOTICE('Configuring mathematically consistent course progress for student...'))

        def set_student_course_progress(student, course, lessons_to_complete_count):
            """
            Enrolls the student in the course and marks precisely `lessons_to_complete_count`
            lessons as completed, then executes `recalculate_progress()` to ensure the
            database percent and completed_at timestamps are 100% synchronized and correct.
            """
            enrollment, _ = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={'progress_percent': 0, 'is_active': True}
            )
            enrollment.is_active = True
            enrollment.save()

            # Retrieve all lessons in proper curricular sequence
            all_course_lessons = list(
                Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
            )
            total_lessons = len(all_course_lessons)

            # Clear any stale progress records for clean recalculation
            LessonProgress.objects.filter(student=student, lesson__module__course=course).delete()

            completed_count = min(lessons_to_complete_count, total_lessons)
            for i in range(completed_count):
                les = all_course_lessons[i]
                LessonProgress.objects.create(
                    student=student,
                    lesson=les,
                    completed=True,
                    completed_at=timezone.now() - timezone.timedelta(days=(total_lessons - i))
                )

            # Recalculate accurately
            percent = enrollment.recalculate_progress()
            self.stdout.write(f'  - Course "{course.title[:35]}...": {completed_count}/{total_lessons} lessons done -> {percent}% progress')
            return enrollment

        # 1. Django Backend Course: 6 of 9 lessons completed (66%)
        set_student_course_progress(student_user, c_django, 6)

        # 2. AI & Deep Learning: 9 of 9 lessons completed (100% Certified Completed!)
        set_student_course_progress(student_user, c_ai, 9)

        # 3. Applied Thermodynamics: 6 of 12 lessons completed (50% in-progress)
        set_student_course_progress(student_user, c_thermo, 6)

        # 4. Digital Signal Processing: 4 of 12 lessons completed (33% in-progress)
        set_student_course_progress(student_user, c_dsp, 4)

        # 5. Structural Dynamics & Seismic Engineering: 12 of 12 lessons completed (100% Certified Completed!)
        set_student_course_progress(student_user, c_civil, 12)

        # 6. Autonomous Mobile Robotics: 3 of 12 lessons completed (25% in-progress)
        set_student_course_progress(student_user, c_robotics, 3)

        # 7. Aerodynamics & Flight Mechanics: Newly enrolled (0 of 12 lessons completed, 0% in-progress)
        set_student_course_progress(student_user, c_aero, 0)

        # Note: Courses 8 (Chemical), 9 (Computer Architecture), and 10 (Biomedical) remain
        # UNENROLLED for Sarah Jenkins so she can explore the catalog and click "Enroll for Free"!

        # =========================================================================
        # 6. Assignments & Quizzes for Courses
        # =========================================================================
        # Mechanical Thermodynamics Assignment
        Assignment.objects.get_or_create(
            course=c_thermo,
            title='Rankine Cycle Thermal Efficiency Analysis',
            defaults={
                'description': 'Calculate the thermal efficiency, back work ratio, and exergy destruction rates for a reheat Rankine cycle operating between boiler pressure 15 MPa and condenser pressure 10 kPa. Include your thermodynamic T-s state diagrams.',
                'due_date': timezone.now() + timezone.timedelta(days=7),
                'max_score': 100,
                'created_by': faculty_elena,
            }
        )

        # DSP Quiz
        q_dsp, q_created = Quiz.objects.get_or_create(
            course=c_dsp,
            title='Nyquist Sampling & Z-Transform Assessment',
            defaults={
                'description': 'Test your comprehension of anti-aliasing criteria, ROC stability, and bilateral Z-plane poles.',
                'duration_minutes': 20,
                'pass_score': 70.0,
                'max_attempts': 3,
                'is_published': True,
                'created_by': faculty_chen,
            }
        )
        if q_created:
            q1 = Question.objects.create(
                quiz=q_dsp,
                text='What is the minimum sampling frequency required to prevent aliasing for an analog signal with maximum frequency component of 18 kHz?',
                explanation='According to the Nyquist-Shannon theorem, the sampling frequency fs must be at least twice the maximum signal frequency (fs >= 2 * fmax = 36 kHz).',
                order=1,
                points=2
            )
            QuestionOption.objects.create(question=q1, text='36 kHz', is_correct=True, order=1)
            QuestionOption.objects.create(question=q1, text='18 kHz', is_correct=False, order=2)
            QuestionOption.objects.create(question=q1, text='72 kHz', is_correct=False, order=3)

            q2 = Question.objects.create(
                quiz=q_dsp,
                text='For a causal discrete-time LTI system to be BIBO stable, what condition must its Z-transform transfer function satisfy?',
                explanation='A causal system is bounded-input bounded-output (BIBO) stable if and only if all poles of H(z) strictly lie inside the unit circle (|z| < 1).',
                order=2,
                points=3
            )
            QuestionOption.objects.create(question=q2, text='All poles of H(z) must strictly lie inside the unit circle (|z| < 1)', is_correct=True, order=1)
            QuestionOption.objects.create(question=q2, text='All zeros must lie outside the unit circle', is_correct=False, order=2)
            QuestionOption.objects.create(question=q2, text='The system must have an equal number of poles and zeros on the imaginary axis', is_correct=False, order=3)

        # Robotics Assignment
        Assignment.objects.get_or_create(
            course=c_robotics,
            title='DH Parameter Table & Forward Kinematics for 6-DOF Arm',
            defaults={
                'description': 'Derive the complete Denavit-Hartenberg parameter table for the UR5 collaborative robotic arm. Formulate the symbolic transformation matrix from base frame {0} to end-effector frame {6}.',
                'due_date': timezone.now() + timezone.timedelta(days=10),
                'max_score': 100,
                'created_by': faculty_chen,
            }
        )

        # Campus Announcements
        Announcement.objects.get_or_create(
            title='Engineering Curriculums & Laboratories Online',
            defaults={
                'content': 'All 10 specialized engineering paths across Mechanical, Electrical, Civil, Aerospace, Robotics, Chemical, and Computer Systems are now available with active progress tracking, interactive lesson viewers, and downloadable materials.',
                'target_role': 'all',
                'created_by': admin_user,
                'is_active': True
            }
        )

        self.stdout.write(self.style.SUCCESS('SmartLearn demonstration data successfully updated with top engineering courses and synchronized progress!'))
