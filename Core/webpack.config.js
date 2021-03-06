var path = require('path');
var webpack = require('webpack');
var PROD = process.env.NODE_ENV=="production";
module.exports = {
  devtool: 'eval',
  entry: {
    editor: [
      //'webpack-dev-server/client?http://localhost:3000',
      //'webpack/hot/only-dev-server',
      './src/editor'
    ],
    index: [
      //'webpack-dev-server/client?http://localhost:3000',
      //'webpack/hot/only-dev-server',
      './src/index'
    ]
  },
  output: {
    path: path.join(__dirname, '/static/dist'),
    filename: '[name].bundle.js',
    publicPath: '/static/'
  },
  plugins: PROD ? [
  ] : [
    new webpack.HotModuleReplacementPlugin()
  ],
  module: {
    loaders: [{
      test: /\.js$/,
      loaders: PROD ? ['babel'] : ['react-hot', 'babel'],
      include: path.join(__dirname, 'src')
    }]
  }
};
