module.exports = {
    content: [
        './templates/*.html',
        './templates/general_configuration/*.html',
        './adminclient/static/adminui/js/**/*.js',
        './adminclient/static/adminui/**/*.css',
        './**/*.py'
    ],
    theme: {
        fontFamily: {
            sans: ["Roboto"] // setting the default font-family
        },
        extend: {
            fontFamily: {
                "roboto": ["Roboto", "sans-serif"], // making possible to use classes font-roboto and font-dancing-script
                "dancing-script": ["Dancing Script", "cursive"],
            },
        },
    },
    plugins: [],
}