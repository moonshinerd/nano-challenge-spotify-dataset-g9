import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, info: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    this.setState({ error, info });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ backgroundColor: '#7f1d1d', color: 'white', padding: '2rem', height: '100vh', width: '100vw', overflow: 'auto' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 'bold' }}>CRASH FATAL! (Render Error)</h1>
          <pre style={{ marginTop: '1rem', whiteSpace: 'pre-wrap' }}>{this.state.error?.toString()}</pre>
          <pre style={{ marginTop: '1rem', whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>{this.state.info?.componentStack}</pre>
          <button onClick={() => window.location.reload()} style={{ marginTop: '1rem', background: 'white', color: 'black', padding: '0.5rem 1rem', borderRadius: '4px' }}>Reload</button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
