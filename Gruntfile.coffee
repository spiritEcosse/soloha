
module.exports = (grunt) ->
    grunt.initConfig(
        pkg: grunt.file.readJSON('package.json')
        coffee:
            compile:
                files:
                    'static_root/src/js/coffee_common/app.js': ['soloha/src/coffee/*.coffee', 'apps/**/*.coffee'],
                    'static/src/js/coffee_common/app.js': ['soloha/src/coffee/*.coffee', 'apps/**/*.coffee']
        less:
            production:
                options:
                    paths: ["assets/css"],
                    sourceMap: true
                files:
                    "static/src/css/main.css": "static/src/less/main.less",
                    "static/oscar/css/styles.css": "static/oscar/less/styles.less",
        cssmin:
            dist:
                files:
                    'static/build/css/style.min.css': ['bower_components/lightslider/dist/css/lightslider.css',
                        'bower_components/yamm/assets/css/yamm.css',
                        "static/djangular/css/bootstrap3.css",
                        "static/djangular/css/styles.css",
                        "bower_components/bootstrap-select/dist/css/bootstrap-select.min.css",
                        'static/oscar/css/styles.css',
                        'static/src/css/**/*.css',
                    ],
        uglify:
            all_src:
                options:
                    sourceMap : true,
                    sourceMapName : 'static/build/js/sourceMap.map'
                    report: 'gzip'
                files:
                    'static/build/js/script.min.js': ["bower_components/jquery/dist/jquery.min.js",
                    'bower_components/bootstrap/dist/js/bootstrap.min.js',
                    'bower_components/angular/angular.js',
                    'static/djangular/js/django-angular.js',
                    'bower_components/angular-resource/angular-resource.js',
                    'bower_components/angular-bootstrap/ui-bootstrap-tpls.min.js',
                    'bower_components/angular-route/angular-route.min.js',
                    'static/oscar/js/oscar/ui.js',
                    'bower_components/lightslider/dist/js/lightslider.min.js',
                    "bower_components/angular-animate/angular-animate.min.js",
                    "bower_components/angular-scroll/angular-scroll.min.js",
                    "static/src/js/**/*.js",
                    "bower_components/blueimp-bootstrap-image-gallery/js/bootstrap-image-gallery.min.js",
                    ]
        imagemin:
            dist:
                files: [{
                    expand: true,
                    cwd: 'static/',
                    src: ['**/*.{png,jpg,gif}'],
                    dest: 'static/'
                }]
    )

    grunt.loadNpmTasks 'grunt-contrib-coffee'
    grunt.loadNpmTasks 'grunt-contrib-less'
    grunt.loadNpmTasks 'grunt-contrib-uglify'
    grunt.loadNpmTasks 'grunt-contrib-cssmin'
    grunt.loadNpmTasks 'grunt-contrib-imagemin'
    grunt.registerTask 'default', ['uglify', 'cssmin', 'imagemin', 'coffee', 'less']
