import * as Yup from "yup";

export const emailValidationSchema = Yup.string().email('Please input a valid email address or leave this field empty!');

export const urlValidationSchema = Yup.string().url('Please input valid URL(s)!').transform((currentValue) => {
  const doesNotStartWithHttp =
    currentValue && !(currentValue.startsWith('http://') || currentValue.startsWith('https://'));
  if (doesNotStartWithHttp) {
    return `https://${currentValue}`;
  }
  return currentValue;
});