import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center gap-6 px-4 py-16">
      <h1 className="font-heading text-4xl font-semibold tracking-tight">Rastro</h1>
      <p className="text-lg text-muted-foreground">
        Acompanhamento das emendas parlamentares federais destinadas a um município, com o estado
        de execução traduzido para linguagem que o morador entende.
      </p>
      <div>
        <Button disabled>Buscar município (em breve)</Button>
      </div>
    </main>
  );
}
