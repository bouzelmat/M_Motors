import { ShapeOptions } from "@mui/system";

export interface ExtendedShapeOptions extends ShapeOptions {
  cardBorderRadius: number;
  inputBorderRadius: number;
  pillBorderRadius: number;
  modalBorderRadius: number;
}

export const shape = {
  borderRadius: 12, // Default input radius
  cardBorderRadius: 20,
  inputBorderRadius: 12,
  pillBorderRadius: 999,
  modalBorderRadius: 24,
};
