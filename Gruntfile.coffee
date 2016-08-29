
module.exports = (grunt) ->
    grunt.initConfig(
        pkg: grunt.file.readJSON('package.json')
        coffee:
            compile:
                files:
                    'static_root/src/js/coffee_common/app.js': ['soloha/src/coffee/*.coffee', 'apps/**/*.coffee'],
                    'static/src/js/coffee_common/app.js': ['soloha/src/coffee/*.coffee', 'apps/**/*.coffee']
        less:
            development:
                options:
                    paths: ["assets/css"],
                files: "static/src/css/main.css": "static/src/less/main.less",
        cssmin:
            dist:
                files:
                    'static/build/css/style.css': ['static/bower_components/lightslider/dist/css/lightslider.css',
                        'static/bower_components/yamm/assets/css/yamm.css',
                        "static/djangular/css/bootstrap3.css",
                        "static/djangular/css/styles.css",
                        "static/bower_components/bootstrap-select/dist/css/bootstrap-select.min.css",
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
                    'static/build/js/script.min.js': ["static/bower_components/jquery/dist/jquery.min.js",
                    'static/bower_components/bootstrap/dist/js/bootstrap.min.js',
                    'static/bower_components/angular/angular.js',
                    'static/djangular/js/django-angular.js',
                    'static/bower_components/angular-resource/angular-resource.js',
                    'static/bower_components/angular-bootstrap/ui-bootstrap-tpls.min.js',
                    'static/bower_components/angular-route/angular-route.min.js',
                    'static/oscar/js/oscar/ui.js',
                    'static/bower_components/lightslider/dist/js/lightslider.min.js',
                    "static/bower_components/angular-animate/angular-animate.min.js",
                    "static/bower_components/angular-scroll/angular-scroll.min.js",
                    "static/src/js/**/*.js",
                    "static/bower_components/blueimp-bootstrap-image-gallery/js/bootstrap-image-gallery.min.js",
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
    grunt.registerTask 'default', ['uglify', 'imagemin', 'cssmin', 'coffee', 'less']


