import React from "react"
import ReactDOM from "react-dom/client"
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material"

import App from "./App"

const theme = createTheme({
	palette: {
		mode: "light",
		primary: {
			main: "#16324f",
		},
		secondary: {
			main: "#f59e0b",
		},
		background: {
			default: "#f4efe8",
		},
	},
	shape: {
		borderRadius: 20,
	},
	typography: {
		fontFamily: ["Inter", "Arial", "sans-serif"].join(","),
	},
})

const rootElement = document.getElementById("root")

if (rootElement === null) {
	throw new Error("Root element not found")
}

ReactDOM.createRoot(rootElement).render(
	<React.StrictMode>
		<ThemeProvider theme={theme}>
			<CssBaseline />
			<App />
		</ThemeProvider>
	</React.StrictMode>,
)
