
		<script type="text/javascript" src="annodoc/head.load.min.js"></script>
		<script type="text/javascript">

	var root = 'annodoc/'; // filled in by jekyll
    head.js(
        // External libraries
        root + 'jquery.min.js',
        root + 'jquery.svg.min.js',
        root + 'jquery.svgdom.min.js',
        root + 'jquery.timeago.js',
        root + 'jquery-ui.min.js',
        root + 'waypoints.min.js',
        root + 'jquery.address.min.js',

        // brat helper modules
        root + 'configuration.js',
        root + 'util.js',
        root + 'annotation_log.js',
        root + 'webfont.js',
        // brat modules
        root + 'dispatcher.js',
        root + 'url_monitor.js',
        root + 'visualizer.js',

        // embedding configuration
        root + 'config.js',
        // project-specific collection data
        root + 'collections.js',

        // NOTE: non-local libraries
        root +'annodoc.js',
        root +'conllu.js'
    );

    var webFontURLs = [
//        root + 'Astloch-Bold.ttf',
        root + 'PT_Sans-Caption-Web-Regular.ttf',
        root + 'Liberation_Sans-Regular.ttf'
    ];

</script>
		