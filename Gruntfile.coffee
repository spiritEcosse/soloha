module.exports = (grunt) ->
  grunt.initConfig(
    pkg: grunt.file.readJSON('package.json')
    coffee:
      files:
        src: [
          'apps/**/*.coffee',
        ],
        dest: 'static/build/js/script.js'
    less:
      development:
        options:
          paths: ["assets/css"],
        files: "static/build/css/main.css": "static/src/less/main.less",
      production:
        options:
          paths: ["assets/css"],
          cleancss: true,
        files: "path/to/result.css": "path/to/source.less"
    min:
      dist:
        src: [
        ],
        dest: ''
    cssmin:
      dist:
        src: [
        ],
        dest: ''
  )

  grunt.loadNpmTasks('grunt-contrib-coffee')
  grunt.loadNpmTasks('grunt-contrib-less')
  #  grunt.loadNpmTasks('grunt-yui-compressor')
  #  grunt.loadNpmTasks('grunt-contrib-imagemin')
  grunt.registerTask('default', ['coffee:files', 'less'])