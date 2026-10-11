import { theme } from "../../src/shared/ui/theme/theme";

describe("Theme Configuration (Ticket 0)", () => {
  it("has light mode as single source of truth", () => {
    expect(theme.palette.mode).toBe("light");
  });

  it("contains exact tokens for backgrounds and accents", () => {
    expect(theme.palette.background.default).toBe("#FFFFFF");
    expect(theme.palette.background.alternate).toBe("#F6F7F8");
    expect(theme.palette.background.studio).toBe("#E9EBEE");
    expect(theme.palette.accent.achat).toBe("#E82127");
    expect(theme.palette.accent.location).toBe("#3B82F6");
    expect(theme.palette.text.primary).toBe("#111113");
  });

  it("configures radii according to shape specifications", () => {
    expect(theme.shape.borderRadius).toBe(12);
  });
});
