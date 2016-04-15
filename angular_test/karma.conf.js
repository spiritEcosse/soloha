module.exports = function(config){
    config.set({

        preprocessors: {
            '**/*.coffee': ['coffee']
        },

        coffeePreprocessor: {
            // options passed to the coffee compiler
            options: {
                bare: true,
                sourceMap: false
            },
            // transforming the filenames
            transformPath: function(path) {
                return path.replace(/\.coffee$/, '.js')
            }
        },

        basePath : '../',

        files : [
            'static/bower_components/angular/angular.js',
            'static/bower_components/angular-route/angular-route.js',
            'static/bower_components/angular-resource/angular-resource.js',
            'static/bower_components/angular-animate/angular-animate.js',
            'static/bower_components/angular-mocks/angular-mocks.js',
            'soloha/**/*.coffee',
            'apps/**/*.coffee',
            'angular_test/apps/**/*.coffee'
        ],

        autoWatch : true,

        frameworks: ['jasmine'],

        browsers : ['Chrome', 'Firefox'],

        plugins : [
            'karma-chrome-launcher',
            'karma-firefox-launcher',
            'karma-jasmine',
            'karma-coffee-preprocessor'
        ],

        junitReporter : {
            outputFile: 'test_out/unit.xml',
            suite: 'unit'
        }

    });
};