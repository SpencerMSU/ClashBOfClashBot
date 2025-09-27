package logger

import (
	"io"
	"os"
	"path/filepath"

	"github.com/sirupsen/logrus"
)

// Logger is the global logger instance
var Logger *logrus.Logger

// InitLogger initializes the global logger - copy from Python main.py logging setup
func InitLogger(debug bool) *logrus.Logger {
	Logger = logrus.New()

	// Set log level
	if debug {
		Logger.SetLevel(logrus.DebugLevel)
	} else {
		Logger.SetLevel(logrus.InfoLevel)
	}

	// Create logs directory if it doesn't exist
	logsDir := "logs"
	if err := os.MkdirAll(logsDir, 0755); err != nil {
		Logger.Warnf("Could not create logs directory: %v", err)
	}

	// Set up file logging
	logFile := filepath.Join(logsDir, "bot.log")
	file, err := os.OpenFile(logFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		Logger.Warnf("Could not open log file: %v", err)
		// Fall back to stdout only
		Logger.SetOutput(os.Stdout)
	} else {
		// Write to both file and console
		multiWriter := io.MultiWriter(os.Stdout, file)
		Logger.SetOutput(multiWriter)
	}

	// Set formatter - similar to Python format
	Logger.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
		TimestampFormat: "2006-01-02 15:04:05",
	})

	// Reduce noise from HTTP clients (similar to Python httpx/httpcore warnings)
	logrus.SetLevel(logrus.WarnLevel)

	Logger.Info("Logger initialized successfully")
	return Logger
}

// GetLogger returns the global logger instance
func GetLogger() *logrus.Logger {
	if Logger == nil {
		return InitLogger(false)
	}
	return Logger
}

// SetLogLevel sets the log level dynamically
func SetLogLevel(level string) {
	switch level {
	case "debug":
		Logger.SetLevel(logrus.DebugLevel)
	case "info":
		Logger.SetLevel(logrus.InfoLevel)
	case "warn":
		Logger.SetLevel(logrus.WarnLevel)
	case "error":
		Logger.SetLevel(logrus.ErrorLevel)
	default:
		Logger.SetLevel(logrus.InfoLevel)
	}
}