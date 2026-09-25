import React, { useCallback, useState } from "react";
import { ActivityIndicator, Alert, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import * as Clipboard from "expo-clipboard";
import { StatusBar } from "expo-status-bar";
import { checkHealth, requestDownload, type MediaType, type Platform, type PlaylistKind } from "./src/api";
import { colors } from "./src/theme";
import SegmentedOption from "./src/components/SegmentedOption";

export default function App() {
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState<Platform>("youtube");
  const [media, setMedia] = useState<MediaType>("video");
  const [kind, setKind] = useState<PlaylistKind>("single");
  const [showOptions, setShowOptions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const paste = useCallback(async () => {
    const text = await Clipboard.getStringAsync();
    if (text) setUrl(text.trim());
  }, []);

  const download = useCallback(async () => {
    if (!url.trim()) {
      Alert.alert("Falta o link", "Cole o link do vídeo ou playlist.");
      return;
    }
    setLoading(true);
    setFeedback(null);
    try {
      const online = await checkHealth();
      if (!online) throw new Error("API fora do ar. Confira EXPO_PUBLIC_API_URL.");
      const r = await requestDownload(platform, media, kind, {
        url: url.trim(),
      });
      const dest = r.destiny ?? r.destino ?? "";
      setFeedback(`OK: ${r.message ?? r.mensagem ?? "Concluido!"}${dest ? `\n${dest}` : ""}`);
    } catch (e) {
      setFeedback(`Erro: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLoading(false);
    }
  }, [url, platform, media, kind]);

  return (
    <View style={s.container}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={s.scroll}>
        <Text style={s.logo}>AV / DOWNLOADER</Text>
        <Text style={s.title}>Seu download, simples.</Text>
        <Text style={s.sub}>Cole um link do YouTube ou do X. O app cuida do resto.</Text>
        <Text style={s.label}>Link do vídeo ou playlist</Text>
        <TextInput
          style={s.input}
          placeholder="https://youtube.com/..."
          placeholderTextColor={colors.grayDark}
          value={url}
          onChangeText={setUrl}
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
          returnKeyType="done"
        />
        <Pressable onPress={paste}><Text style={s.link}>Colar da area de transferencia</Text></Pressable>
        <Pressable onPress={() => setShowOptions((value) => !value)}>
          <Text style={s.optionsToggle}>{showOptions ? "Ocultar opções" : "Mais opções"}</Text>
        </Pressable>
        {showOptions && (
          <View style={s.options}>
            <Text style={s.label}>Plataforma</Text>
            <View style={s.row}>
              <SegmentedOption label="YouTube" selected={platform === "youtube"} onPress={() => setPlatform("youtube")} />
              <SegmentedOption label="X / Twitter" selected={platform === "x"} onPress={() => { setPlatform("x"); setKind("single"); }} />
            </View>
            <Text style={s.label}>Formato</Text>
            <View style={s.row}>
              <SegmentedOption label="MP4 Video" selected={media === "video"} onPress={() => setMedia("video")} />
              <SegmentedOption label="MP3 Audio" selected={media === "audio"} onPress={() => setMedia("audio")} />
            </View>
            {platform === "youtube" && (
              <View>
                <Text style={s.label}>Tipo</Text>
                <View style={s.row}>
                  <SegmentedOption label="Unico" selected={kind === "single"} onPress={() => setKind("single")} />
                  <SegmentedOption label="Playlist" selected={kind === "playlist"} onPress={() => setKind("playlist")} />
                </View>
              </View>
            )}
          </View>
        )}
        <Text style={s.defaultHint}>Os arquivos são salvos na pasta padrão configurada na API.</Text>
        <Pressable style={[s.cta, loading && s.off]} onPress={download} disabled={loading}>
          {loading ? <ActivityIndicator color={colors.white} /> : <Text style={s.ctaTx}>Baixar {media === "video" ? "MP4" : "MP3"}</Text>}
        </Pressable>
        {feedback && <Text style={s.fb}>{feedback}</Text>}
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: 24, paddingTop: 72, paddingBottom: 40, gap: 10 },
  logo: { color: colors.primary, fontWeight: "800", fontSize: 12, letterSpacing: 2, marginBottom: 8 },
  title: { color: colors.white, fontSize: 30, lineHeight: 36, fontWeight: "800" },
  sub: { color: colors.gray, fontSize: 15, lineHeight: 22, marginBottom: 18 },
  label: { color: colors.grayLight, fontWeight: "700", marginTop: 8, marginBottom: 2 },
  input: {
    backgroundColor: colors.graphite,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 15,
    color: colors.white,
    fontSize: 16,
  },
  link: { color: colors.blue, fontSize: 14, marginTop: 2, marginBottom: 6 },
  row: { flexDirection: "row", gap: 8, marginTop: 6 },
  cta: { marginTop: 20, backgroundColor: colors.primary, borderRadius: 12, paddingVertical: 16, alignItems: "center" },
  off: { opacity: 0.6 },
  ctaTx: { color: colors.white, fontWeight: "800", fontSize: 16 },
  fb: { marginTop: 16, backgroundColor: colors.graphiteLight, color: colors.white, padding: 14, borderRadius: 12, lineHeight: 20 },
  optionsToggle: { color: colors.blue, fontSize: 14, fontWeight: "600", marginTop: 14 },
  options: { marginTop: 4, padding: 16, backgroundColor: colors.graphite, borderRadius: 12, borderWidth: 1, borderColor: colors.border },
  defaultHint: { color: colors.gray, fontSize: 12, lineHeight: 18, marginTop: 12 },
});
