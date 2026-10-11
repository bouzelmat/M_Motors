import "@mui/material/styles";

declare module "@mui/material/styles" {
  interface TypeBackground {
    alternate: string;
    studio: string;
  }

  interface Palette {
    surface: {
      card: string;
      nested: string;
    };
    border: {
      subtle: string;
      strong: string;
    };
    accent: {
      achat: string;
      location: string;
    };
    glass: {
      bg: string;
    };
  }

  interface PaletteOptions {
    surface?: {
      card?: string;
      nested?: string;
    };
    border?: {
      subtle?: string;
      strong?: string;
    };
    accent?: {
      achat?: string;
      location?: string;
    };
    glass?: {
      bg?: string;
    };
  }
}
