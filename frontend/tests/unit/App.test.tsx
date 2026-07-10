import { render, screen } from "@testing-library/react"

import App from "../../src/App"

describe("App", () => {
  it("renders the main product heading", () => {
    render(<App />)

    expect(
      screen.getByRole("heading", {
        name: /déploiement automatisé, validation continue/i,
      }),
    ).toBeInTheDocument()
  })
})