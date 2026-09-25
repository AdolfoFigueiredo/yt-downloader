import React from "react";
import { Pressable, StyleSheet, Text } from "react-native";
import { colors } from "../theme";

interface Props {
  label: string;
  selected: boolean;
  onPress: () => void;
}

export default function SegmentedOption({ label, selected, onPress }: Props) {
  return (
    <Pressable
      onPress={onPress}
      style={[styles.btn, selected && styles.btnActive]}
    >
      <Text style={[styles.text, selected && styles.textActive]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.graphite,
    alignItems: "center",
  },
  btnActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  text: { color: colors.grayLight, fontWeight: "600" },
  textActive: { color: colors.white },
});
