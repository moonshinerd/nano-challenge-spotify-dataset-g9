const babel = require('@babel/core');
const fs = require('fs');

const code = fs.readFileSync('src/App.jsx', 'utf-8');
try {
  babel.transformSync(code, {
    presets: ['@babel/preset-react']
  });
  console.log("JSX is valid!");
} catch (e) {
  console.error("Syntax Error:", e.message);
}
