const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {  
  entry: {
    'site-base': './assets/site-base.js',  // Base styles
    'site-bootstrap': './assets/site-bootstrap.js',  // Bootstrap styles and overrides
    app: './assets/js/app.js',  // path to our input file
  },
  output: {
    path: path.resolve(__dirname, './static'),  // path to our Django static directory
    filename: 'js/[name]-bundle.js',  // output bundle file name    
  },
  devtool: "source-map",
  module: {
    rules: [
      {
        test: /\.(js)$/,
        exclude: /node_modules/,
        loader: "babel-loader"
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader',
        ],
      },
      {
        mimetype: 'image/svg+xml',
        scheme: 'data',
        type: 'asset/resource',
        generator: {
          filename: 'icons/[hash].svg'
        }
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      'filename': 'css/[name].css',
    }),
  ],
  optimization: {
    minimizer: [new TerserPlugin({
      extractComments: false,  // disable generation of license.txt files
    })],
  },
};