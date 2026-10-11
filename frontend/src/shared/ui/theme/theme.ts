import { createTheme } from "@mui/material/styles";
import { palette } from "./palette";
import { typography } from "./typography";
import { shape } from "./shape";
import { componentsOverride } from "./overrides/components";

let baseTheme = createTheme({
  palette,
  typography,
  shape,
});

export const theme = createTheme(baseTheme, {
  components: componentsOverride(baseTheme),
});

export default theme;
