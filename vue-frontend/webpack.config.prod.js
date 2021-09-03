'use strict'
const { VueLoaderPlugin } = require('vue-loader')
var path = require('path');
module.exports = {
  mode: 'production',
  entry: [
    './src/app.js'
  ],
  output: {
    library: 'voting',
    libraryTarget: 'umd',
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'static/js/')
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        use: 'vue-loader'
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          'css-loader',
        ]
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin()
  ]
}
