import React from "react";

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = {
    hasError: false,
    message: "",
  };

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      message: error.message,
    };
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return <div className="error-boundary">Unexpected error: {this.state.message}</div>;
    }

    return this.props.children;
  }
}
